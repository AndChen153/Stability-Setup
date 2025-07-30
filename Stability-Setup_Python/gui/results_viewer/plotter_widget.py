# plotter.py
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from labellines import labelLines
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QScrollArea,
    QLabel,
    QPushButton,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Qt
from helper.global_helpers import get_logger

#TODO: add raw current/current density measurement
#TODO: force tight layout
class PlotterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        # These dictionaries keep track of our legend state.
        self.line_label_texts = {}
        self.legend_groups = {}
        self.legend_checkboxes = {}
        self.group_checkboxes = {}
        self.line_to_group = {}

    def _init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # A container widget to hold the plot canvas, toolbar, and legend.
        self.plot_container = QWidget(self)
        self.plot_container_layout = QVBoxLayout(self.plot_container)
        self.plot_container_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.plot_container)

    def update_plot(self, plot_title: str, csv_files):
        """Loads CSV files from the given folder, creates the plot,
        and builds the canvas, toolbar, and custom legend widget."""

        if not csv_files:
            get_logger().log("No CSV files found in folder.")
            return

        # Clear any previous content.
        self._clear_layout(self.plot_container_layout)

        # Create the plot.
        fig, ax = plt.subplots(tight_layout=True)

        # Decide which plotting logic to use.
        if "mppt" in os.path.basename(csv_files[0]).lower():
            self._plot_mppt(ax, csv_files, plot_title)
        else:
            self._plot_scan(ax, csv_files, plot_title)

        # Build the canvas and toolbar.
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar = NavigationToolbar(canvas, self)

        # Create the custom legend widget.
        legend_widget = self.create_legend_widget(ax)
        legend_widget.setFixedWidth(160)
        legend_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Create statistics table for both scan and mppt plots
        stats_widget = None
        if "mppt" in os.path.basename(csv_files[0]).lower():
            stats_widget = self.create_mppt_stats_table(csv_files)
            stats_widget.setMinimumWidth(300)  # Set minimum width instead of fixed
            stats_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            stats_widget = self.create_scan_stats_table(csv_files)
            stats_widget.setMinimumWidth(300)  # Set minimum width instead of fixed
            stats_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Layout the canvas, toolbar, legend, and stats.
        main_splitter = QSplitter(Qt.Horizontal)

        # Left side: plot only (resizable)
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(canvas)

        main_splitter.addWidget(legend_widget)
        main_splitter.addWidget(plot_widget)
        # Right side: statistics table (resizable)
        if stats_widget:
            main_splitter.addWidget(stats_widget)
            # Set initial sizes: plot=500, legend=250 (fixed), stats=400
            # main_splitter.setSizes([250, 500, 400])
        else:
            # Set initial sizes: plot=700, legend=250 (fixed)
            main_splitter.setSizes([700, 250])

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(toolbar)
        v_layout.addWidget(main_splitter, 1)

        widget_container = QWidget()
        widget_container.setLayout(v_layout)

        self.plot_container_layout.addWidget(widget_container)

        canvas.draw()
        plt.close(fig)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _plot_mppt(self, ax, csv_files, plot_title):
        overall_min_time, overall_max_time, overall_max_pce = None, None, None

        # Get a color cycle for different CSV files
        # Use tab10 for up to 10 files, then cycle through or use other colormaps
        if len(csv_files) <= 10:
            # For small numbers, use specific indices to get maximally distinct colors
            color_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9][:len(csv_files)]
            colors = [plt.cm.tab10(i/9.0) for i in color_indices]
        else:
            # For more than 10 files, use a continuous colormap that can generate many distinct colors
            colors = plt.cm.hsv(np.linspace(0, 1, len(csv_files), endpoint=False))

        for file_idx, csv_file in enumerate(csv_files):
            arr = np.loadtxt(csv_file, delimiter=",", dtype=str)
            header_row = np.where(arr == "Time")[0][0]

            meta_data = {}
            for data in arr[:header_row, :2]:
                meta_data[data[0]] = data[1]

            headers = arr[header_row, :]
            arr = arr[header_row + 1 :, :]

            header_dict = {value: index for index, value in enumerate(headers)}
            pixel_V = arr[:, 1::2][:, 0:8].astype(float)
            pixel_mA = arr[:, 2::2][:, 0:8].astype(float)
            time = np.array(arr[:, header_dict["Time"]]).astype("float")
            if len(time) < 1:
                return

            cell_area = float(meta_data["Cell Area (mm^2)"])

            data = ((pixel_V*pixel_mA/1000) / (0.1*cell_area))*100

            # Sample data if necessary
            if len(time) > 5000:
                step = int(np.ceil(len(time) / 5000))
                time = time[::step]
                data = data[::step, :]

            time = time / 60.0  # convert to minutes from seconds

            if overall_min_time is None:
                overall_min_time = min(time)
                overall_max_time = max(time)
            else:
                overall_min_time = min(overall_min_time, min(time))
                overall_max_time = max(overall_max_time, max(time))

            if overall_max_pce is None:
                overall_max_pce = np.max(data)
            else:
                overall_max_pce = max(overall_max_pce, np.max(data))

            if overall_max_time > 60:
                time /= 60.0
                overall_max_time /= 60
                ax.set_xlabel("Time [hrs]")
            else:
                ax.set_xlabel("Time [min]")

            # Plot each pixel.
            NUM_PIXELS = data.shape[1]
            file_color = colors[file_idx]
            for i in range(NUM_PIXELS):
                basename = os.path.basename(csv_file)
                match = re.search(r"ID(\d+)", basename, re.IGNORECASE)
                id_str = match.group(1) if match else ""
                label_suffix = f" (ID {id_str})" if id_str else ""
                lineName = f"Pixel {i+1}{label_suffix}"
                ax.plot(time, data[:, i], label=lineName, color=file_color)

        if overall_min_time is None or overall_max_time is None:
            overall_min_time, overall_max_time = 0, 1

        ax.set_xlim(overall_min_time * 0.99, overall_max_time * 1.01)
        ax.set_ylim(0, overall_max_pce*1.15)
        ax.set_title(plot_title)
        ax.set_ylabel("PCE [%]")
        ax.grid(True)

        # Create line labels.
        self.line_label_texts = {}
        lines = ax.get_lines()
        if lines:
            x_min, x_max = ax.get_xlim()
            xvals = np.linspace(
                x_min + 0.1 * (x_max - x_min), x_max - 0.1 * (x_max - x_min), len(lines)
            )
            bold_font = FontProperties(weight="medium")
            label_texts = labelLines(
                lines,
                xvals=xvals,
                zorder=2.5,
                align=False,
                fontsize=11,
                fontproperties=bold_font,
            )
            self.line_label_texts = dict(zip(lines, label_texts))

    def _plot_scan(self, ax, csv_files, plot_title):
        # Get a color cycle for different CSV files
        # Use tab10 for up to 10 files, then cycle through or use other colormaps
        if len(csv_files) <= 10:
            # For small numbers, use specific indices to get maximally distinct colors
            color_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9][:len(csv_files)]
            colors = [plt.cm.tab10(i/9.0) for i in color_indices]
        else:
            # For more than 10 files, use a continuous colormap that can generate many distinct colors
            colors = plt.cm.hsv(np.linspace(0, 1, len(csv_files), endpoint=False))

        for file_idx, csv_file in enumerate(csv_files):
            try:
                arr = np.loadtxt(csv_file, delimiter=",", dtype=str)
                header_row = np.where(arr == "Time")[0][0]

                meta_data = {}
                for data in arr[:header_row, :2]:
                    meta_data[data[0]] = data[1]

                arr = arr[header_row + 1 :, :]
                data = arr[:, 2:-1] # Gets rid of time and voltage applied columns
                pixel_V = data[:, ::2].astype(float)
                pixel_mA = data[:, 1::2].astype(float)
                # if ("Cell Area (mm^2)" in meta_data):
                #     pixel_mA /= float(meta_data["Cell Area (mm^2)"])
                # else:
                #     pixel_mA /= 0.128
                jvLen = pixel_V.shape[0] // 2
                file_color = colors[file_idx]

                for i in range(pixel_V.shape[1]):
                    basename = os.path.basename(csv_file)
                    match = re.search(r"ID(\d+)", basename, re.IGNORECASE)
                    id_str = match.group(1) if match else ""
                    label_suffix = f" (ID {id_str})" if id_str else ""

                    # Split voltage and current data into two halves
                    V_first_half = pixel_V[0:jvLen, i]
                    I_first_half = pixel_mA[0:jvLen, i]

                    V_second_half = pixel_V[jvLen:, i]
                    I_second_half = pixel_mA[jvLen:, i]

                    # Determine which half is forward (increasing voltage) and which is reverse (decreasing voltage)
                    first_half_trend = np.polyfit(range(len(V_first_half)), V_first_half, 1)[0] if len(V_first_half) > 1 else 0
                    second_half_trend = np.polyfit(range(len(V_second_half)), V_second_half, 1)[0] if len(V_second_half) > 1 else 0

                    # Assign forward and reverse based on voltage trends
                    if first_half_trend > second_half_trend:
                        # First half is forward (increasing), second half is reverse (decreasing)
                        V_forward, I_forward = V_first_half, I_first_half
                        V_reverse, I_reverse = V_second_half, I_second_half
                    else:
                        # Second half is forward (increasing), first half is reverse (decreasing)
                        V_forward, I_forward = V_second_half, I_second_half
                        V_reverse, I_reverse = V_first_half, I_first_half

                    # Plot reverse sweep (solid line)
                    ax.plot(
                        V_reverse,
                        I_reverse,
                        color=file_color,
                        label=f"Pixel {i+1} Reverse{label_suffix}",
                    )

                    # Plot forward sweep (dashed line)
                    ax.plot(
                        V_forward,
                        I_forward,
                        "--",
                        color=file_color,
                        label=f"Pixel {i+1} Forward{label_suffix}",
                    )

            except Exception as e:
                get_logger().log(f"Error processing file {csv_file}: {e}")

        ax.set_title(plot_title)
        ax.set_xlabel("Bias [V]")
        ax.set_ylabel("Jmeas [mAcm-2]")
        ax.grid(True)
        ax.spines["bottom"].set_position("zero")

    def scan_calcs(self, arr, headers, cell_area):
        """
        returns: reverse:[fillFactorListSplit, jscListSplit, vocListSplit], forward:[fillFactorListSplit, jscListSplit, vocListSplit]
        """
        dead_pixels = self.get_dead_pixels(arr, headers)

        length = len(headers) - 1

        jvList = []

        for i in range(2, length):
            jvList.append(arr[:, i])

        jList = []  # current
        vList = []  # voltage
        for i in range(0, len(jvList), 2):
            jList.append([float(j) for j in jvList[i + 1]])
            vList.append([float(x) for x in jvList[i]])

        jList = np.array(jList).T
        vList = np.array(vList).T
        jListReverse, jListForward = np.array_split(jList, 2)
        vListReverse, vListForward = np.array_split(vList, 2)

        return (
            self.calc(jListReverse, vListReverse, cell_area, dead_pixels),
            self.calc(jListForward, vListForward, cell_area, dead_pixels),
        )

    def calc(self, jList, vList, cell_area, dead_pixels):
        # find Jsc (V = 0)
        jscList = np.zeros((vList.shape[1]))
        for i in range(vList.shape[1]):
            difference_array = np.absolute(vList[:, i])
            idx = difference_array.argmin()
            jscList[i] = jList[idx, i]

        # find Voc (J = 0)
        vocList = np.zeros((jList.shape[1]))
        for i in range(jList.shape[1]):
            difference_array = np.absolute(jList[:, i])
            idx = difference_array.argmin()
            vocList[i] = vList[idx, i]

        # find Fill Factor
        pce_list = jList * vList
        maxVIdx = np.argmax(pce_list, axis=0)  # find index of max pce value
        vmppList = []
        jmppList = []
        for i in range(len(maxVIdx)):  # for i in number of pixels
            # if vList[maxVIdx[i],i]>0:
            vmppList.append(vList[maxVIdx[i], i])
            jmppList.append(jList[maxVIdx[i], i])
        vmppList = np.array(vmppList)
        jmppList = np.array(jmppList)

        fillFactorList = 100 * vmppList * jmppList / (jscList * vocList)
        jscList = jscList / cell_area

        fillFactorList = np.delete(fillFactorList, dead_pixels)
        jscList = np.delete(jscList, dead_pixels)
        vocList = np.delete(vocList, dead_pixels)

        # fillFactorList, jscList, vocList
        return (fillFactorList, jscList, vocList)

    def getDeadPixels(self, arr, headers):
        length = len(headers) - 1

        jvList = []
        for i in range(2, length):  # remove timing and volts output
            jvList.append(arr[:, i])

        dead_pixels = []
        for i in range(0, len(jvList), 2):
            # get_logger().log(i)
            # get_logger().log(jvList[i], jvList[i+1])
            jvList[i] = [float(j) for j in jvList[i]]
            jvList[i + 1] = [float(x) for x in jvList[i + 1]]
            if (
                np.mean(np.absolute(np.array(jvList[i]))) < 0.2
                or np.mean(np.absolute(np.array(jvList[i + 1]))) < 0.2
            ):
                dead_pixels.append(int(i / 2))  # [9, 12, 13, 19, 21, 27, 30, 31]

        return dead_pixels

    def create_legend_widget(self, ax):
        """Creates a custom legend with checkboxes to toggle line visibility."""
        legend_widget = QWidget()
        legend_layout = QVBoxLayout(legend_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)

        # Top buttons: Show All / Hide All.
        top_buttons_layout = QHBoxLayout()
        show_all_button = QPushButton("Show All")
        show_all_button.clicked.connect(lambda: self.show_all(ax))
        top_buttons_layout.addWidget(show_all_button)
        hide_all_button = QPushButton("Hide All")
        hide_all_button.clicked.connect(lambda: self.hide_all(ax))
        top_buttons_layout.addWidget(hide_all_button)
        legend_layout.addLayout(top_buttons_layout)

        # Scroll area for the legend entries.
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        inner_widget = QWidget()
        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setContentsMargins(0, 0, 0, 0)

        # Group lines by ID extracted from the label.
        groups = {}
        self.line_to_group = {}
        ungrouped = []
        for line in ax.get_lines():
            label = line.get_label()
            match = re.search(r"\(ID (\d+)\)|ID(\d+)", label, re.IGNORECASE)
            if match:
                group_id = (
                    match.group(1) if match.group(1) is not None else match.group(2)
                )
                groups.setdefault(group_id, []).append(line)
                self.line_to_group[line] = group_id
            else:
                ungrouped.append(line)

        self.legend_groups = groups
        self.legend_checkboxes = {}
        self.group_checkboxes = {}

        # Create checkboxes for each group.
        for group_id, lines in sorted(groups.items(), key=lambda x: int(x[0])):
            group_checkbox = QCheckBox(f"ID {group_id}")
            all_visible = all(line.get_visible() for line in lines)
            none_visible = all(not line.get_visible() for line in lines)
            group_checkbox.blockSignals(True)
            if all_visible:
                group_checkbox.setCheckState(Qt.Checked)
            elif none_visible:
                group_checkbox.setCheckState(Qt.Unchecked)
            else:
                group_checkbox.setTristate(True)
                group_checkbox.setCheckState(Qt.PartiallyChecked)
            group_checkbox.blockSignals(False)
            group_checkbox.toggled.connect(
                lambda checked, gid=group_id: self.toggle_group_visibility(gid, checked)
            )
            self.group_checkboxes[group_id] = group_checkbox
            inner_layout.addWidget(group_checkbox)

            # Create indented checkboxes for each line in the group.
            group_layout = QVBoxLayout()
            group_layout.setContentsMargins(20, 0, 0, 0)
            for line in lines:
                label_clean = re.sub(r"\s*\(ID \d+\)", "", line.get_label())
                label_clean = re.sub(r"ID\d+", "", label_clean)
                checkbox = QCheckBox(label_clean)
                checkbox.setChecked(line.get_visible())
                checkbox.toggled.connect(
                    lambda checked, l=line: self.toggle_line_visibility(l, checked)
                )
                group_layout.addWidget(checkbox)
                self.legend_checkboxes[line] = checkbox
            inner_layout.addLayout(group_layout)

        # Add ungrouped lines.
        if ungrouped:
            ungrouped_label = QLabel("Ungrouped:")
            inner_layout.addWidget(ungrouped_label)
            for line in ungrouped:
                checkbox = QCheckBox(line.get_label())
                checkbox.setChecked(line.get_visible())
                checkbox.toggled.connect(
                    lambda checked, l=line: self.toggle_line_visibility(l, checked)
                )
                inner_layout.addWidget(checkbox)
                self.legend_checkboxes[line] = checkbox

        inner_layout.addStretch()
        scroll_area.setWidget(inner_widget)
        legend_layout.addWidget(scroll_area)
        return legend_widget

    def create_scan_stats_table(self, csv_files):
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
                file_stats = self.calculate_scan_stats(csv_file)
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
        table.setSortingEnabled(True)

        stats_layout.addWidget(table)
        return stats_widget

    def calculate_scan_stats(self, csv_file):
        """Calculate statistics for all pixels in a single CSV file."""
        try:
            arr = np.loadtxt(csv_file, delimiter=",", dtype=str)
            header_row = np.where(arr == "Time")[0][0]

            meta_data = {}
            for data in arr[:header_row, :2]:
                meta_data[data[0]] = data[1]

            arr = arr[header_row + 1:, :]
            data = arr[:, 2:-1] # Gets rid of time and voltage applied columns
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
                # Calculate voltage trends for each half
                first_half_trend = np.polyfit(range(len(V_first_half)), V_first_half, 1)[0] if len(V_first_half) > 1 else 0
                second_half_trend = np.polyfit(range(len(V_second_half)), V_second_half, 1)[0] if len(V_second_half) > 1 else 0

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
                    reverse_stats = self.get_stats(V_reverse, I_reverse)
                    stats_list.append({
                        "file_id": file_id,
                        "pixel": pixel_idx + 1,
                        "sweep": "Reverse",
                        "FF": reverse_stats["FF"] * 100,  # Convert to percentage
                        "PCE": reverse_stats["PCE"],
                        "Jsc": abs(reverse_stats["Jsc"]),  # Take absolute value
                        "Voc": reverse_stats["Voc"]
                    })
                except Exception as e:
                    get_logger().log(f"Error calculating reverse stats for pixel {pixel_idx + 1}: {e}")

                # Calculate stats for forward sweep
                try:
                    forward_stats = self.get_stats(V_forward, I_forward)
                    stats_list.append({
                        "file_id": file_id,
                        "pixel": pixel_idx + 1,
                        "sweep": "Forward",
                        "FF": forward_stats["FF"] * 100,  # Convert to percentage
                        "PCE": forward_stats["PCE"],
                        "Jsc": abs(forward_stats["Jsc"]),  # Take absolute value
                        "Voc": forward_stats["Voc"]
                    })
                except Exception as e:
                    get_logger().log(f"Error calculating forward stats for pixel {pixel_idx + 1}: {e}")

            return stats_list

        except Exception as e:
            get_logger().log(f"Error processing file {csv_file}: {e}")
            return []

    def get_stats(self, voltage, current):
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

        return {
            "FF": FF,
            "PCE": PCE,
            "Jsc": Jsc,
            "Voc": Voc
        }

    def create_mppt_stats_table(self, csv_files):
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
                file_stats = self.calculate_mppt_file_stats(csv_file)
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
        table.setColumnCount(4)  # File ID, Pixel, Last 30s PCE, Highest 30s Avg PCE, Degradation %
        table.setHorizontalHeaderLabels([
            "Pixel", "PCE Highest 30s","PCE Final 30s",  "Degradation"
        ])

        # Populate table
        for row, stats in enumerate(all_stats):
            table.setItem(row, 0, QTableWidgetItem(f"ID{stats['file_id']} Pixel {stats['pixel']}"))
            table.setItem(row, 1, QTableWidgetItem(f"{stats['pce_highest_30s_avg']:.2f}%"))
            table.setItem(row, 2, QTableWidgetItem(f"{stats['pce_last_30s_avg']:.2f}%"))
            table.setItem(row, 3, QTableWidgetItem(f"{stats['degradation_percent']:.2f}%"))

        # Configure table appearance
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSortingEnabled(True)

        stats_layout.addWidget(table)
        return stats_widget

    def calculate_mppt_file_stats(self, csv_file):
        """Calculate MPPT statistics for all pixels in a single CSV file."""
        try:
            arr = np.loadtxt(csv_file, delimiter=",", dtype=str)
            header_row = np.where(arr == "Time")[0][0]

            meta_data = {}
            for data in arr[:header_row, :2]:
                meta_data[data[0]] = data[1]

            headers = arr[header_row, :]
            arr = arr[header_row + 1:, :]

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

                # Calculate statistics for this pixel
                pce_last_30s_avg = self.calculate_pce_last_30s(time_minutes, pixel_pce)
                pce_highest_30s_avg = self.calculate_pce_highest_30s_avg(time_minutes, pixel_pce)

                # Calculate degradation percentage
                if pce_highest_30s_avg > 0:
                    degradation_percent = ((pce_highest_30s_avg - pce_last_30s_avg) / pce_highest_30s_avg) * 100
                else:
                    degradation_percent = 0.0

                stats_list.append({
                    "file_id": file_id,
                    "pixel": pixel_idx + 1,
                    "pce_last_30s_avg": pce_last_30s_avg,
                    "pce_highest_30s_avg": pce_highest_30s_avg,
                    "degradation_percent": degradation_percent
                })

            return stats_list

        except Exception as e:
            get_logger().log(f"Error processing MPPT file {csv_file}: {e}")
            return []

    def calculate_pce_last_30s(self, time_minutes, pce_data):
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

    def calculate_pce_first_30s(self, time_minutes, pce_data):
        """Calculate average PCE in the last 30 seconds of data."""
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return 0.0

        # Find indices for the last 30 seconds
        mask = time_minutes >= (0.5)

        if np.sum(mask) == 0:
            # If no data in last 30 seconds, return the last value
            return float(pce_data[-1]) if len(pce_data) > 0 else 0.0

        # Calculate average PCE in last 30 seconds
        first_30s_pce = pce_data[mask]
        return float(np.mean(first_30s_pce))

    def calculate_pce_highest_30s_avg(self, time_minutes, pce_data):
        """Calculate the average of 30 seconds of PCE values around the highest PCE point."""
        if len(time_minutes) == 0 or len(pce_data) == 0:
            return 0.0

        # Convert 30 seconds to minutes
        window_minutes = 0.5

        # If total time is less than 30 seconds, use all data
        total_time = np.max(time_minutes) - np.min(time_minutes)
        if total_time <= window_minutes:
            return float(np.mean(pce_data))

        # Find the index of the highest PCE value
        max_pce_idx = np.argmax(pce_data)
        peak_time = time_minutes[max_pce_idx]

        # Define the 30-second window around the peak (±15 seconds)
        half_window = window_minutes / 2
        start_time = peak_time - half_window
        end_time = peak_time + half_window

        # Find data points within the 30-second window around the peak
        mask = (time_minutes >= start_time) & (time_minutes <= end_time)

        if np.sum(mask) > 0:
            window_pce = pce_data[mask]
            return float(np.mean(window_pce))
        else:
            # Fallback: if no data in window, return the peak value itself
            return float(pce_data[max_pce_idx])

    def toggle_group_visibility(self, group_id, checked):
        """Toggles the visibility of all lines in the group."""
        for line in self.legend_groups.get(group_id, []):
            line.set_visible(checked)
            if line in self.line_label_texts:
                self.line_label_texts[line].set_visible(checked)
            checkbox = self.legend_checkboxes.get(line)
            if checkbox:
                checkbox.blockSignals(True)
                checkbox.setChecked(checked)
                checkbox.blockSignals(False)
        group_checkbox = self.group_checkboxes.get(group_id)
        if group_checkbox:
            group_checkbox.blockSignals(True)
            group_checkbox.setTristate(False)
            group_checkbox.setChecked(checked)
            group_checkbox.blockSignals(False)
        self._redraw_canvas()

    def update_group_checkbox(self, group_id):
        group_checkbox = self.group_checkboxes.get(group_id)
        lines = self.legend_groups.get(group_id, [])
        all_visible = all(line.get_visible() for line in lines)
        none_visible = all(not line.get_visible() for line in lines)
        group_checkbox.blockSignals(True)
        if all_visible:
            group_checkbox.setTristate(False)
            group_checkbox.setChecked(True)
        elif none_visible:
            group_checkbox.setTristate(False)
            group_checkbox.setChecked(False)
        else:
            group_checkbox.setTristate(True)
            group_checkbox.setCheckState(Qt.PartiallyChecked)
        group_checkbox.blockSignals(False)

    def toggle_line_visibility(self, line, visible):
        """Toggles an individual line's visibility."""
        line.set_visible(visible)
        if line in self.line_label_texts:
            self.line_label_texts[line].set_visible(visible)
        if line in self.line_to_group:
            self.update_group_checkbox(self.line_to_group[line])
        self._redraw_canvas()

    def show_all(self, ax):
        """Shows all lines and updates checkboxes accordingly."""
        for line in ax.get_lines():
            line.set_visible(True)
            if line in self.line_label_texts:
                self.line_label_texts[line].set_visible(True)
        for checkbox in self.legend_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)
        for group_checkbox in self.group_checkboxes.values():
            group_checkbox.blockSignals(True)
            group_checkbox.setTristate(False)
            group_checkbox.setChecked(True)
            group_checkbox.blockSignals(False)
        self._redraw_canvas()

    def hide_all(self, ax):
        """Hides all lines and updates checkboxes accordingly."""
        for line in ax.get_lines():
            line.set_visible(False)
            if line in self.line_label_texts:
                self.line_label_texts[line].set_visible(False)
        for checkbox in self.legend_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        for group_checkbox in self.group_checkboxes.values():
            group_checkbox.blockSignals(True)
            group_checkbox.setTristate(False)
            group_checkbox.setChecked(False)
            group_checkbox.blockSignals(False)
        self._redraw_canvas()

    def _redraw_canvas(self):
        # Assuming the canvas is a child of our plot_container.
        canvas = self.findChild(FigureCanvas)
        if canvas:
            canvas.draw_idle()

