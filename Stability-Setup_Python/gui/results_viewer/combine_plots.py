import os
import csv
from datetime import datetime
from typing import List, Dict
from helper.global_helpers import get_logger
from constants import Constants
import numpy as np

MINIMUM_MINUTES = 20

def discover_mppt_files(folder_path: str) -> List[str]:
    """
    Discover compressed MPPT CSV files in the specified folder.

    Args:
        folder_path: Path to the directory to search

    Returns:
        List of full file paths for compressed MPPT files
    """
    if not os.path.isdir(folder_path):
        get_logger().log(f"Invalid directory: {folder_path}")
        return []

    mppt_files = []
    try:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith("compressedmppt.csv"):
                full_path = os.path.join(folder_path, filename)
                mppt_files.append(full_path)

        get_logger().log(f"Found {len(mppt_files)} compressed MPPT files in {folder_path}")
        return sorted(mppt_files)

    except Exception as e:
        get_logger().log(f"Error discovering MPPT files: {e}")
        return []

def parse_filename_components(filepath: str) -> Dict[str, str]:
    """
    Parse filename components from MPPT file path.

    Expected format: {date}_{time}__{ID}__{type}.csv
    Example: Jul-30-2025_13-44-33__ID1__mppt.csv

    Args:
        filepath: Full path to the file

    Returns:
        Dictionary with parsed components: date, time, id, type, filename
    """
    filename = os.path.basename(filepath)

    try:
        # Split by double underscore to get main components
        parts = filename.split("__")

        if len(parts) < 3:
            get_logger().log(f"Unexpected filename format: {filename}")
            return {}

        # Extract date and time from first part
        datetime_part = parts[0]
        date_time_parts = datetime_part.split("_")

        if len(date_time_parts) >= 2:
            date = date_time_parts[0]
            time = "_".join(date_time_parts[1:])
        else:
            date = datetime_part
            time = ""

        # Extract ID
        id_part = parts[1]

        # Extract type (remove .csv extension)
        type_part = parts[2].replace(".csv", "")

        return {
            "date": date,
            "time": time,
            "id": id_part,
            "type": type_part,
            "filename": filename,
            "filepath": filepath
        }

    except Exception as e:
        get_logger().log(f"Error parsing filename {filename}: {e}")
        return {}

def categorize_by_id_and_datetime(files: List[str]) -> Dict[str, List[Dict]]:
    """
    Categorize MPPT files by ID, keeping all files for each ID regardless of date/time.

    Args:
        files: List of file paths

    Returns:
        Dictionary: {id: [list_of_file_info_dicts]}
    """
    categorized = {}

    for filepath in files:
        file_info = parse_filename_components(filepath)

        if not file_info:
            continue

        id_key = file_info["id"]

        # Initialize list for this ID if needed
        if id_key not in categorized:
            categorized[id_key] = []

        categorized[id_key].append(file_info)

    get_logger().log(f"Categorized files by ID: {len(categorized)} IDs found")
    for id_key, file_list in categorized.items():
        get_logger().log(f"  {id_key}: {len(file_list)} files")

    return categorized

def check_total_time_threshold(filepath: str, threshold: float = 20.0) -> bool:
    """
    Check if the "Total Time" parameter in the CSV file header is above the threshold.

    Args:
        filepath: Path to the CSV file
        threshold: Minimum value for Total Time (default: 20.0)

    Returns:
        True if Total Time > threshold, False otherwise
    """
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)

            # Read the header rows to find the Total Time parameter
            for row_num, row in enumerate(reader):
                if len(row) >= 2 and row[0] == Constants.time_param:
                    try:
                        total_time_value = float(row[1])
                        is_above_threshold = total_time_value > threshold
                        get_logger().log(f"File {filepath}: Total Time = {total_time_value}, Above threshold ({threshold}): {is_above_threshold}")
                        return is_above_threshold
                    except (ValueError, IndexError):
                        get_logger().log(f"Error parsing Total Time value in {filepath}: {row[1] if len(row) > 1 else 'missing'}")
                        return False

                # Stop searching after a reasonable number of header rows
                if row_num > 20:
                    break

            get_logger().log(f"Total Time parameter not found in {filepath}")
            return False

    except Exception as e:
        get_logger().log(f"Error reading file {filepath}: {e}")
        return False

def select_compressed_mppt_file(file_group: List[Dict]) -> str:
    """
    Select the compressed MPPT file from a group.

    Args:
        file_group: List of file info dictionaries for the same date/ID

    Returns:
        Path to the compressed MPPT file
    """
    for file_info in file_group:
        if file_info["type"] == "compressedmppt":
            get_logger().log(f"Using compressed file: {file_info['filename']}")
            return file_info["filepath"]

    # This shouldn't happen since we only discover compressed files
    get_logger().log("No compressed MPPT file found in group")
    return ""

def load_and_validate_mppt_file(file_path):
    """
    Load a single MPPT CSV file and extract metadata and data.

    Args:
        file_path (str): Path to CSV file

    Returns:
        tuple: (metadata, headers, data_array)
    """
    print(f"Loading {os.path.basename(file_path)}...")

    # Load the file as string array
    arr = np.loadtxt(file_path, delimiter=",", dtype=str)

    # Find the header row (contains "Time")
    header_row_idx = np.where(arr == "Time")[0]
    if len(header_row_idx) == 0:
        raise ValueError(f"No 'Time' column found in {file_path}")

    header_row = header_row_idx[0]

    # Extract components
    headers = arr[header_row, :]
    metadata = arr[:header_row + 1, :]
    data = arr[header_row + 1:, :]

    # Convert data to appropriate types
    data_numeric = data.astype(float)

    print(f"  - Data shape: {data_numeric.shape}")
    print(f"  - Time range: {data_numeric[0, 0]:.1f} to {data_numeric[-1, 0]:.1f} seconds")

    return metadata, headers, data_numeric

def stitch_mppt_files(file_paths, output_filename=None):
    """
    Stitch multiple MPPT CSV files into a continuous time series.
    Removes all rows containing NaN values before combining.

    Args:
        file_paths (list): List of file paths to stitch
        output_filename (str): Optional output filename

    Returns:
        tuple: (combined_metadata, headers, combined_data)
    """
    if not file_paths:
        raise ValueError("No files provided")

    get_logger().log(f"Stitching {len(file_paths)} files...")

    combined_data_list = []
    cumulative_time = 0.0
    reference_metadata = None
    reference_headers = None

    for i, file_path in enumerate(file_paths):
        metadata, headers, data = load_and_validate_mppt_file(file_path)

        # Remove rows with NaN values
        nan_mask = np.isnan(data).any(axis=1)
        clean_data = data[~nan_mask]

        rows_removed = len(data) - len(clean_data)
        if rows_removed > 0:
            get_logger().log(f"Removed {rows_removed} rows with NaN values from {os.path.basename(file_path)}")

        # Store reference metadata and headers from first file
        if i == 0:
            reference_metadata = metadata
            reference_headers = headers
            # For first file, include all clean data
            combined_data_list.append(clean_data)
            cumulative_time = clean_data[-1, 0]
        else:
            # Validate headers match
            if not np.array_equal(headers, reference_headers):
                get_logger().log(f"Warning: Headers in {os.path.basename(file_path)} don't match reference")

            # For subsequent files, adjust time column and skip some initial rows to avoid overlap
            data_copy = clean_data.copy()
            data_copy[:, 0] += cumulative_time

            # Skip first few rows to avoid overlap, but keep the time continuity
            skip_rows = min(5, len(data_copy) // 10)  # Skip 5 rows or 10% of data, whichever is smaller
            combined_data_list.append(data_copy[skip_rows:, :])

            # Update cumulative time for next file
            cumulative_time = data_copy[-1, 0]

        get_logger().log(f"File {i+1}: {len(clean_data)} clean data points (removed {rows_removed} NaN rows), time range: {clean_data[0, 0]:.1f} to {clean_data[-1, 0]:.1f} s")

    # Combine all data
    combined_data = np.vstack(combined_data_list)

    # Final check for any remaining NaN values
    final_nan_mask = np.isnan(combined_data).any(axis=1)
    if np.any(final_nan_mask):
        final_clean_data = combined_data[~final_nan_mask]
        final_rows_removed = len(combined_data) - len(final_clean_data)
        get_logger().log(f"Removed {final_rows_removed} additional rows with NaN values from combined data")
        combined_data = final_clean_data

    get_logger().log(f"Combined dataset:")
    get_logger().log(f"  - Total data points: {combined_data.shape[0]}")
    get_logger().log(f"  - Total time span: {combined_data[-1, 0]:.1f} seconds ({combined_data[-1, 0]/3600:.2f} hours)")
    get_logger().log(f"  - Columns: {len(reference_headers)}")

    # Save combined file if requested
    if output_filename:
        save_combined_data(reference_metadata, reference_headers, combined_data, output_filename)

    return reference_metadata, reference_headers, combined_data

def save_combined_data(metadata, headers, data, output_filename):
    """
    Save the combined data to a CSV file.
    Updates the Total Time header value to match the actual combined file duration.

    Args:
        metadata (np.array): Metadata from original files
        headers (np.array): Column headers
        data (np.array): Combined numeric data
        output_filename (str): Output filename
    """
    # Calculate the actual total time from the combined data
    actual_total_time_seconds = data[-1, 0] - data[0, 0]
    actual_total_time_minutes = actual_total_time_seconds / 60.0

    get_logger().log(f"Updating Total Time header: {actual_total_time_minutes:.2f} minutes")

    # Update the Total Time value in metadata
    updated_metadata = metadata.copy()
    for i, row in enumerate(updated_metadata):
        if len(row) >= 2 and row[0] == Constants.time_param:
            updated_metadata[i, 1] = str(actual_total_time_minutes)
            get_logger().log(f"Updated Total Time from {row[1]} to {actual_total_time_minutes:.2f}")
            break

    # Convert data back to string format for saving
    data_str = data.astype(str)

    # Combine updated metadata, headers, and data
    full_array = np.vstack([updated_metadata, data_str])

    # Save to file
    np.savetxt(output_filename, full_array, delimiter=',', fmt='%s')

    print(f"\nCombined data saved to: {output_filename}")
    print(f"File size: {os.path.getsize(output_filename) / (1024*1024):.2f} MB")
    get_logger().log(f"Updated Total Time header to {actual_total_time_minutes:.2f} minutes")

def combine_plots_main(folder_path: str) -> Dict[str, List[str]]:
    """
    Main function to discover, categorize, and combine MPPT plots.
    Groups by ID first, then includes all files for each ID sorted chronologically.
    Only includes files where Total Time > 20.
    Creates stitched combined files for each ID.

    Args:
        folder_path: Path to directory containing MPPT files

    Returns:
        Dictionary suitable for plot grouping: {id: [combined_file_path]}
    """
    get_logger().log(f"Starting combine plots for folder: {folder_path}")

    # Step 1: Discover all compressed MPPT files
    mppt_files = discover_mppt_files(folder_path)
    get_logger().log(f"mppt files to combine: {mppt_files}")

    if not mppt_files:
        get_logger().log("No compressed MPPT files found")
        return {}

    # Step 2: Filter files based on Total Time threshold
    filtered_files = []
    for filepath in mppt_files:
        if check_total_time_threshold(filepath, threshold=MINIMUM_MINUTES):
            filtered_files.append(filepath)
        else:
            get_logger().log(f"Excluding file {filepath} - Total Time <= 20")

    if not filtered_files:
        get_logger().log(f"No files found with Total Time > {MINIMUM_MINUTES}")
        return {}

    get_logger().log(f"Filtered to {len(filtered_files)} files with Total Time > 20")

    # Step 3: Categorize by ID (all files for each ID)
    categorized = categorize_by_id_and_datetime(filtered_files)

    # Step 4: Create combined files for each ID
    plot_groups = {}

    for id_key, file_list in categorized.items():
        # Sort files chronologically by datetime using the full filename
        # This ensures proper chronological order since filenames contain datetime stamps
        def sort_key(file_info):
            datetime_str = file_info['filename'].split('__')[0]
            return datetime.strptime(datetime_str, '%b-%d-%Y_%H-%M-%S')

        sorted_files = sorted(file_list, key=sort_key)
        id_files = [file_info['filepath'] for file_info in sorted_files]

        get_logger().log(f"Sorted files for {id_key}: {[f['filename'] for f in sorted_files]}")

        if id_files and len(id_files) > 1:
            # Create combined file for this ID
            try:
                # Generate output filename: Combined__{ID}__compressedmppt.csv
                output_filename = os.path.join(folder_path, f"Combined__{id_key}__mppt.csv")

                get_logger().log(f"Stitching {len(id_files)} files for {id_key}")
                get_logger().log(f"Files to stitch: {[os.path.basename(f) for f in id_files]}")

                # Stitch the files together
                metadata, headers, combined_data = stitch_mppt_files(id_files, output_filename)

                # Add the combined file to plot groups
                plot_groups[id_key] = [output_filename]
                get_logger().log(f"Created combined file for {id_key}: {output_filename}")

            except Exception as e:
                get_logger().log(f"Error stitching files for {id_key}: {e}")
                # Fallback to individual files if stitching fails
                plot_groups[id_key] = id_files

        elif id_files:
            # Single file - no need to combine
            plot_groups[id_key] = id_files
            get_logger().log(f"Single file for {id_key}, no combining needed")

    get_logger().log(f"Created {len(plot_groups)} ID-based plot groups")
    return plot_groups
