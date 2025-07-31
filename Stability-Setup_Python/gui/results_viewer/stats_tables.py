# stats_tables.py
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from helper.global_helpers import get_logger
from .calculations import ScanCalculations, MPPTCalculations


class StatsTableFactory:
    """Factory class for creating statistics tables for scan and MPPT data."""
    
    @staticmethod
    def create_scan_stats_table(csv_files):
        """Creates a table widget displaying photovoltaic statistics for each pixel."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("Photovoltaic Statistics")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(title_label)

        # Create table
        table = QTableWidget()

        # Calculate statistics for all files
        all_stats = []
        for csv_file in csv_files:
            try:
                file_stats = ScanCalculations.calculate_scan_stats(csv_file)
                if file_stats:
                    all_stats.extend(file_stats)
            except Exception as e:
                get_logger().log(f"Error calculating stats for {csv_file}: {e}")

        if not all_stats:
            # No data to display
            no_data_label = QLabel("No statistics available")
            stats_layout.addWidget(no_data_label)
            return stats_widget

        # Set up table structure
        table.setRowCount(len(all_stats))
        table.setColumnCount(6)  # File ID, Pixel, Sweep, FF, PCE, Jsc, Voc
        table.setHorizontalHeaderLabels([
            "Pixel", "Sweep", "FF (%)", "PCE (%)", "Jsc (mA/cm²)", "Voc (V)"
        ])

        # Populate table
        for row, stats in enumerate(all_stats):
            table.setItem(row, 0, QTableWidgetItem(f"ID{stats['file_id']} Pixel {stats['pixel']}"))
            table.setItem(row, 1, QTableWidgetItem(stats["sweep"]))
            table.setItem(row, 2, QTableWidgetItem(f"{stats['FF']:.2f}"))
            table.setItem(row, 3, QTableWidgetItem(f"{stats['PCE']:.2f}"))
            table.setItem(row, 4, QTableWidgetItem(f"{stats['Jsc']:.2f}"))
            table.setItem(row, 5, QTableWidgetItem(f"{stats['Voc']:.3f}"))

        # Configure table appearance
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSortingEnabled(False)

        stats_layout.addWidget(table)
        return stats_widget

    @staticmethod
    def create_mppt_stats_table(csv_files):
        """Creates a table widget displaying MPPT statistics for each pixel."""
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setContentsMargins(5, 5, 5, 5)

        # Title
        title_label = QLabel("MPPT Statistics")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(title_label)

        # Create table
        table = QTableWidget()

        # Calculate MPPT statistics for all files
        all_stats = []
        for csv_file in csv_files:
            try:
                file_stats = MPPTCalculations.calculate_mppt_file_stats(csv_file)
                if file_stats:
                    all_stats.extend(file_stats)
            except Exception as e:
                get_logger().log(f"Error calculating MPPT stats for {csv_file}: {e}")

        if not all_stats:
            # No data to display
            no_data_label = QLabel("No MPPT statistics available")
            stats_layout.addWidget(no_data_label)
            return stats_widget

        # Set up table structure
        table.setRowCount(len(all_stats))
        table.setColumnCount(5)  # Pixel, Last 30s PCE, Highest 30s Avg PCE, Degradation %, T90
        table.setHorizontalHeaderLabels([
            "Pixel", "PCE Highest 30s", "PCE Final 30s", "Degradation", "T90 (hrs)"
        ])

        # Populate table
        for row, stats in enumerate(all_stats):
            table.setItem(row, 0, QTableWidgetItem(f"ID{stats['file_id']} Pixel {stats['pixel']}"))
            table.setItem(row, 1, QTableWidgetItem(f"{stats['pce_highest_30s_avg']:.2f}%"))
            table.setItem(row, 2, QTableWidgetItem(f"{stats['pce_last_30s_avg']:.2f}%"))
            table.setItem(row, 3, QTableWidgetItem(f"{stats['degradation_percent']:.2f}%"))

            # Format T90 display
            t90_value = stats['t90_hours']
            if t90_value == float('inf'):
                t90_display = "N/A"
            else:
                t90_display = f"{t90_value:.1f}"
            table.setItem(row, 4, QTableWidgetItem(t90_display))

        # Configure table appearance
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSortingEnabled(False)

        stats_layout.addWidget(table)
        return stats_widget
