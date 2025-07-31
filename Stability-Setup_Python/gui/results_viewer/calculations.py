# calculations.py
import os
import re
import numpy as np
from helper.global_helpers import get_logger

class ScanCalculations:
    """Handles all calculations related to scan data analysis."""

    @staticmethod
    def get_stats(voltage, current):
        """Calculate photovoltaic statistics for a single pixel's I-V curve.

        Args:
            voltage: 1D array of voltage values
            current: 1D array of current values

        Returns:
            dict: Dictionary containing FF, PCE, Jsc, and Voc values
        """
        V = np.asarray(voltage)
        I = np.asarray(current)
        if V.shape != I.shape:
            raise ValueError("voltages and currents must have the same shape")

        # 1) Voc: interpolate V at I=0
        sort_I = np.argsort(I)
        I_sorted = I[sort_I]
        V_sorted_by_I = V[sort_I]
        Voc = float(np.interp(0.0, I_sorted, V_sorted_by_I))

        # 2) Jsc: interpolate I at V=0
        sort_V = np.argsort(V)
        V_sorted = V[sort_V]
        I_sorted_by_V = I[sort_V]
        Jsc = float(np.interp(0.0, V_sorted, I_sorted_by_V))

        # 3) Maximum power point
        P = V * I
        idx_mp = np.argmax(P)
        Vmp = float(V[idx_mp])
        Imp = float(I[idx_mp])

        # 4) Fill Factor
        FF = (Vmp * Imp) / (Voc * Jsc) if (Voc * Jsc) != 0 else np.nan

        # 5) PCE (assuming 100 mW/cm² illumination)
        PCE = (Vmp * Imp) / 100 * 100

        return {"FF": FF, "PCE": PCE, "Jsc": Jsc, "Voc": Voc}

    @staticmethod
    def calculate_scan_stats(csv_file):
        """Calculate statistics for all pixels in a single CSV file."""
        try:
            arr = np.loadtxt(csv_file, delimiter=",", dtype=str)
            header_row = np.where(arr == "Time")[0][0]

            meta_data = {}
            for data in arr[:header_row, :2]:
                meta_data[data[0]] = data[1]

            arr = arr[header_row + 1 :, :]
            data = arr[:, 2:-1]  # Gets rid of time and voltage applied columns
            pixel_V = data[:, ::2].astype(float)
            pixel_mA = data[:, 1::2].astype(float)

            # Get cell area for current density calculation
            cell_area = float(meta_data.get("Cell Area (mm^2)", 0.128))

            # Convert to current density (mA/cm²)
            pixel_mA_cm2 = pixel_mA / cell_area

            # Split data into two halves
            jvLen = pixel_V.shape[0] // 2

            # Extract file ID from filename
            basename = os.path.basename(csv_file)
            match = re.search(r"ID(\d+)", basename, re.IGNORECASE)
            file_id = match.group(1) if match else "Unknown"

            stats_list = []

            # Process each pixel
            for pixel_idx in range(pixel_V.shape[1]):
                # Split voltage and current data into two halves
                V_first_half = pixel_V[0:jvLen, pixel_idx]
                I_first_half = pixel_mA_cm2[0:jvLen, pixel_idx]

                V_second_half = pixel_V[jvLen:, pixel_idx]
                I_second_half = pixel_mA_cm2[jvLen:, pixel_idx]

                # Determine which half is forward (increasing voltage) and which is reverse (decreasing voltage)
                first_half_trend = (
                    np.polyfit(range(len(V_first_half)), V_first_half, 1)[0]
                    if len(V_first_half) > 1
                    else 0
                )
                second_half_trend = (
                    np.polyfit(range(len(V_second_half)), V_second_half, 1)[0]
                    if len(V_second_half) > 1
                    else 0
                )

                # Assign forward (increasing voltage) and reverse (decreasing voltage) based on trends
                if first_half_trend > second_half_trend:
                    # First half is forward (increasing), second half is reverse (decreasing)
                    V_forward, I_forward = V_first_half, I_first_half
                    V_reverse, I_reverse = V_second_half, I_second_half
                else:
                    # Second half is forward (increasing), first half is reverse (decreasing)
                    V_forward, I_forward = V_second_half, I_second_half
                    V_reverse, I_reverse = V_first_half, I_first_half

                # Calculate stats for reverse sweep
                try:
                    reverse_stats = ScanCalculations.get_stats(V_reverse, I_reverse)
                    stats_list.append(
                        {
                            "file_id": file_id,
                            "pixel": pixel_idx + 1,
                            "sweep": "Reverse",
                            "FF": reverse_stats["FF"] * 100,  # Convert to percentage
                            "PCE": reverse_stats["PCE"],
                            "Jsc": abs(reverse_stats["Jsc"]),  # Take absolute value
                            "Voc": reverse_stats["Voc"],
                        }
                    )
                except Exception as e:
                    get_logger().log(
                        f"Error calculating reverse stats for pixel {pixel_idx + 1}: {e}"
                    )

                # Calculate stats for forward sweep
                try:
                    forward_stats = ScanCalculations.get_stats(V_forward, I_forward)
                    stats_list.append(
                        {
                            "file_id": file_id,
                            "pixel": pixel_idx + 1,
                            "sweep": "Forward",
                            "FF": forward_stats["FF"] * 100,  # Convert to percentage
                            "PCE": forward_stats["PCE"],
                            "Jsc": abs(forward_stats["Jsc"]),  # Take absolute value
                            "Voc": forward_stats["Voc"],
                        }
                    )
                except Exception as e:
                    get_logger().log(
                        f"Error calculating forward stats for pixel {pixel_idx + 1}: {e}"
                    )

            return stats_list

        except Exception as e:
            get_logger().log(f"Error processing file {csv_file}: {e}")
            return []


class MPPTCalculations:
    """Handles all calculations related to MPPT data analysis."""

    @staticmethod
    def calculate_mppt_file_stats(csv_file):
        """Calculate MPPT statistics for all pixels in a single CSV file."""
        try:
            arr = np.loadtxt(csv_file, delimiter=",", dtype=str)
        except Exception as e:
            get_logger().log(f"Error processing MPPT file {csv_file}: {e}")
            return []


        header_row = np.where(arr == "Time")[0][0]

        meta_data = {}
        for data in arr[:header_row, :2]:
            meta_data[data[0]] = data[1]

        headers = arr[header_row, :]
        arr = arr[header_row + 1 :, :]

        header_dict = {value: index for index, value in enumerate(headers)}
        if "Time" not in header_dict:
            get_logger().log(f"'Time' header not found in {csv_file}")
            return []

        pixel_V = arr[:, 1::2][:, 0:8].astype(float)
        pixel_mA = arr[:, 2::2][:, 0:8].astype(float)
        time = np.array(arr[:, header_dict["Time"]]).astype("float")

        if len(time) < 1:
            return []

        # Get cell area for PCE calculation
        cell_area = float(meta_data.get("Cell Area (mm^2)", 0.128))

        # Calculate PCE for each pixel: (V * I / 1000) / (0.1 * cell_area) * 100
        data = ((pixel_V * pixel_mA / 1000) / (0.1 * cell_area)) * 100
        # Convert time to minutes
        time_minutes = time / 60.0

        # Extract file ID from filename
        basename = os.path.basename(csv_file)
        match = re.search(r"ID(\d+)", basename, re.IGNORECASE)
        file_id = match.group(1) if match else "Unknown"

        stats_list = []

        # Process each pixel
        NUM_PIXELS = data.shape[1]
        for pixel_idx in range(NUM_PIXELS):
            pixel_pce = data[:, pixel_idx]

            idx_stable = MPPTCalculations.detect_mppt_stable(pixel_pce, time_minutes)

            pixel_pce_stable = pixel_pce[idx_stable:]
            time_minutes_stable = time_minutes[idx_stable:]

            # Calculate statistics for this pixel
            pce_last_30s_avg = MPPTCalculations.calculate_pce_last_30s(
                time_minutes_stable, pixel_pce_stable
            )
            pce_first_30s_avg =MPPTCalculations.calculate_pce_first_30s(
                    time_minutes_stable, pixel_pce_stable
                )
            t90_hours = MPPTCalculations.calculate_t90_hours(
                time_minutes_stable, pixel_pce_stable, pce_first_30s_avg
            )

            # Calculate degradation percentage
            if pce_first_30s_avg > 0:
                degradation_percent = (
                    (pce_first_30s_avg - pce_last_30s_avg) / pce_first_30s_avg
                ) * 100
            else:
                degradation_percent = 0.0

            stats_list.append(
                {
                    "file_id": file_id,
                    "pixel": pixel_idx + 1,
                    "pce_last_30s_avg": pce_last_30s_avg,
                    "pce_first_30s_avg": pce_first_30s_avg,
                    "degradation_percent": degradation_percent,
                    "t90_hours": t90_hours,
                }
            )

        return stats_list


    @staticmethod
    def calculate_pce_last_30s(time_minutes, pce_data):
        """Calculate average PCE in the last 30 seconds of data."""
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return 0.0

        # Convert 30 seconds to minutes
        last_30s_minutes = 0.5
        max_time = np.max(time_minutes)

        # Find indices for the last 30 seconds
        mask = time_minutes >= (max_time - last_30s_minutes)

        if np.sum(mask) == 0:
            # If no data in last 30 seconds, return the last value
            return float(pce_data[-1]) if len(pce_data) > 0 else 0.0

        # Calculate average PCE in last 30 seconds
        last_30s_pce = pce_data[mask]
        return float(np.mean(last_30s_pce))

    @staticmethod
    def calculate_pce_first_30s(time_minutes, pce_data):
        """Calculate average PCE in the first 30 seconds of data."""
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return 0.0

        # Find indices for the first 30 seconds
        mask = time_minutes <= 0.5

        if np.sum(mask) == 0:
            # If no data in first 30 seconds, return the first value
            return float(pce_data[0]) if len(pce_data) > 0 else 0.0

        # Calculate average PCE in first 30 seconds
        first_30s_pce = pce_data[mask]
        return float(np.mean(first_30s_pce))

    @staticmethod
    def calculate_t90_hours(time_minutes, pce_data, pce_first_30s_avg):
        """Calculate T90: time to reach 90% of highest 30s average PCE (10% degradation).
        Only looks for degradation after the peak PCE point.
        """
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return float("inf")  # Return infinity if no data

        if pce_first_30s_avg <= 0:
            return float("inf")

        # Calculate 90% of initial PCE (10% degradation threshold)
        target_pce = pce_first_30s_avg * 0.9

        # Find the first time when PCE drops to or below 90% of initial (after peak)
        degraded_indices = np.where(pce_data <= target_pce)[0]

        if len(degraded_indices) == 0:
            # PCE never dropped to 90% after peak, return infinity
            return float("inf")

        first_degraded_idx = degraded_indices[0]
        return float(time_minutes[first_degraded_idx] / 60)

    @staticmethod
    def detect_mppt_stable(pce, time_min):
        win_pts_smooth = 11                           # must be odd; tweak as needed
        kernel = np.ones(win_pts_smooth, dtype=float) / win_pts_smooth
        pce_smooth = np.convolve(pce, kernel, mode='same')

        # ------------------------------------------------------------------
        # 2)  Instantaneous slope  (% per minute) --------------------------
        # ------------------------------------------------------------------
        dpdt = np.gradient(pce_smooth, time_min)      # d(pce)/d(time)

        # ------------------------------------------------------------------
        # 3)  Threshold that means “steady” -------------------------------
        # ------------------------------------------------------------------
        # ------------------------------------------------------------------
        # 4)  Require a full N-minute window below the threshold ----------
        # ------------------------------------------------------------------
        window_minutes = 0.5                          # how long it must stay flat
        noise = np.std(pce_smooth[-50:])          # last 50 points on the plateau
        slope_thresh = noise / window_minutes     # ≈ 0.5 × 10⁻³ to 2 × 10⁻³ %/min
        mask = np.abs(dpdt) < slope_thresh            # Boolean array

        # sample rate (points / minute) from the median spacing
        Fs = 1.0 / np.median(np.diff(time_min))
        win_pts = max(int(round(window_minutes * Fs)), 1)

        # running sum of the True/False mask
        run_sum = np.convolve(mask.astype(int),
                            np.ones(win_pts, dtype=int),
                            mode='valid')

        # first index where *all* points in the window are True
        stable_candidates = np.where(run_sum == win_pts)[0]

        if stable_candidates.size:
            idx0 = stable_candidates[0]               # start of the first stable window
        else:
            idx0 = 0

        return idx0
