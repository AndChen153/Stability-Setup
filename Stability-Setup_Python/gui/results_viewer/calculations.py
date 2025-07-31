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
            t_idx, t_sec = MPPTCalculations.detect_mppt_stable_irregular(
                data, time, W_sec=10.0, hold_sec=4.0, eps_roc=2e-3, eps_cv=5e-3
            )
            get_logger().log(f"t_idx: {t_idx}, t_sec: {t_sec}")

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

                # Calculate statistics for this pixel
                pce_last_30s_avg = MPPTCalculations.calculate_pce_last_30s(
                    time_minutes, pixel_pce
                )
                pce_highest_30s_avg, max_pce_idx = (
                    MPPTCalculations.calculate_pce_highest_30s_avg(
                        time_minutes, pixel_pce
                    )
                )
                t90_hours = MPPTCalculations.calculate_t90_hours(
                    time_minutes, pixel_pce, pce_highest_30s_avg, max_pce_idx
                )

                # Calculate degradation percentage
                if pce_highest_30s_avg > 0:
                    degradation_percent = (
                        (pce_highest_30s_avg - pce_last_30s_avg) / pce_highest_30s_avg
                    ) * 100
                else:
                    degradation_percent = 0.0

                stats_list.append(
                    {
                        "file_id": file_id,
                        "pixel": pixel_idx + 1,
                        "pce_last_30s_avg": pce_last_30s_avg,
                        "pce_highest_30s_avg": pce_highest_30s_avg,
                        "degradation_percent": degradation_percent,
                        "t90_hours": t90_hours,
                    }
                )

            return stats_list

        except Exception as e:
            get_logger().log(f"Error processing MPPT file {csv_file}: {e}")
            return []

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
    def calculate_pce_highest_30s_avg(time_minutes, pce_data):
        """Calculate the average of 30 seconds of PCE values around the highest PCE point.

        Returns:
            tuple: (average_pce, max_pce_idx) where max_pce_idx is the index of the highest PCE value
        """
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return 0.0, 0

        # Convert 30 seconds to minutes
        window_minutes = 0.5

        # Find the index of the highest PCE value
        max_pce_idx = np.argmax(pce_data)

        # If total time is less than 30 seconds, use all data
        total_time = np.max(time_minutes) - np.min(time_minutes)
        if total_time <= window_minutes:
            return float(np.mean(pce_data)), max_pce_idx

        peak_time = time_minutes[max_pce_idx]

        # Define the 30-second window around the peak (±15 seconds)
        half_window = window_minutes / 2
        start_time = peak_time - half_window
        end_time = peak_time + half_window

        # Find data points within the 30-second window around the peak
        mask = (time_minutes >= start_time) & (time_minutes <= end_time)

        if np.sum(mask) > 0:
            window_pce = pce_data[mask]
            return float(np.mean(window_pce)), max_pce_idx
        else:
            # Fallback: if no data in window, return the peak value itself
            return float(pce_data[max_pce_idx]), max_pce_idx

    @staticmethod
    def calculate_t90_hours(time_minutes, pce_data, pce_highest_30s_avg, max_pce_idx):
        """Calculate T90: time to reach 90% of highest 30s average PCE (10% degradation).
        Only looks for degradation after the peak PCE point.
        """
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return float("inf")  # Return infinity if no data

        if pce_highest_30s_avg <= 0:
            return float("inf")

        # Calculate 90% of initial PCE (10% degradation threshold)
        target_pce = pce_highest_30s_avg * 0.9

        # Only look for degradation after the peak PCE point
        post_peak_pce = pce_data[max_pce_idx:]
        post_peak_time = time_minutes[max_pce_idx:]

        # Find the first time when PCE drops to or below 90% of initial (after peak)
        degraded_indices = np.where(post_peak_pce <= target_pce)[0]

        if len(degraded_indices) == 0:
            # PCE never dropped to 90% after peak, return infinity
            return float("inf")

        first_degraded_idx = degraded_indices[0]
        return float(post_peak_time[first_degraded_idx] / 60)

    @staticmethod
    def detect_mppt_stable_irregular(Y, t, W_sec, hold_sec, eps_roc, eps_cv):
        # Y: (n, T), t: (T,), increasing
        Y = Y.T
        Y = np.asarray(Y)
        n, T = Y.shape
        t = np.asarray(t, dtype=np.float64)

        # 1) window start per k for a W_sec time window
        k0 = np.searchsorted(t, t - W_sec, side="left")

        # 2) prefix sums (rowwise for Y-derived arrays)
        def ps(a):
            return np.pad(np.cumsum(a, axis=1, dtype=np.float64), ((0, 0), (1, 0)))

        S_y = ps(Y)
        S_y2 = ps(Y * Y)
        S_ty = ps(Y * t)  # t broadcasts over rows

        S_t = np.pad(np.cumsum(t, dtype=np.float64), (1, 0))
        S_t2 = np.pad(np.cumsum(t * t, dtype=np.float64), (1, 0))

        # 3) gather rolling sums for each end index k using start k0[k]
        idx = np.arange(T)

        def take_roll(S, rowwise=True):
            if rowwise:  # S: (n, T+1)
                return S[:, idx + 1] - S[:, k0]
            else:  # S: (T+1,)
                return S[idx + 1] - S[k0]

        sum_y = take_roll(S_y, rowwise=True)  # (n, T)
        sum_y2 = take_roll(S_y2, rowwise=True)  # (n, T)
        sum_ty = take_roll(S_ty, rowwise=True)  # (n, T)
        sum_t = take_roll(S_t, rowwise=False)  # (T,)
        sum_t2 = take_roll(S_t2, rowwise=False)  # (T,)

        # 4) slope + stats per window
        w = idx - k0 + 1  # samples per window (T,)

        denom = (w * sum_t2) - (sum_t**2)  # (T,)
        mean = sum_y / w
        var = (sum_y2 / w) - mean * mean
        var = np.maximum(var, 0.0)
        cv = np.sqrt(var) / (mean + 1e-12)

        slope = ((w * sum_ty) - (sum_t * sum_y)) / (denom + 1e-12)  # per second

        stable = (np.abs(slope) <= eps_roc * mean) & (cv <= eps_cv)

        # 5) require stability to persist for hold_sec
        k_hold = np.searchsorted(t, t - hold_sec, side="left")
        S_stable = np.pad(np.cumsum(stable.astype(np.int32), axis=1), ((0, 0), (1, 0)))
        consec = S_stable[:, idx + 1] - S_stable[:, k_hold]  # (n, T)
        ok = consec >= (idx - k_hold + 1)  # all samples in last hold_sec stable

        # 6) first time per trace
        first = np.argmax(ok, axis=1)  # 0 if none
        has = ok.any(axis=1)
        first = np.where(has, first, -1)
        t_idx = first
        t_sec = np.where(first >= 0, t[first], np.nan)

        return t_idx.astype(int), t_sec
