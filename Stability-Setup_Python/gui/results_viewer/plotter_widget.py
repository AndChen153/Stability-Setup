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
    QSplitter,
    QRadioButton,
    QButtonGroup,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtCore import Qt
from helper.global_helpers import get_logger
from .stats_tables import StatsTableFactory

#TODO: add raw current/current density measurement
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
        # Store data for replotting when display mode changes
        self.current_csv_files = []
        self.current_plot_title = ""
        self.current_ax = None
        self.current_canvas = None

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

        # Store data for replotting
        self.current_csv_files = csv_files
        self.current_plot_title = plot_title

        # Clear any previous content.
        self._clear_layout(self.plot_container_layout)
        self.mppt = False

        # Create the plot.
        fig, ax = plt.subplots(tight_layout=True)
        self.current_ax = ax

        # Decide which plotting logic to use.
        if "mppt" in os.path.basename(csv_files[0]).lower():
            self._plot_mppt(ax, csv_files, plot_title)
            self.mppt = True
        else:
            self._plot_scan(ax, csv_files, plot_title)

        # Build the canvas and toolbar.
        canvas = FigureCanvas(fig)
        self.current_canvas = canvas
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar = NavigationToolbar(canvas, self)

        # Create the custom legend widget.
        legend_widget = self.create_legend_widget(ax, self.mppt)
        legend_widget.setFixedWidth(160)
        legend_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Create statistics table for both scan and mppt plots
        stats_widget = None
        if "combined" in os.path.basename(csv_files[0]).lower():
            pass
        elif "mppt" in os.path.basename(csv_files[0]).lower():
            stats_widget = StatsTableFactory.create_mppt_stats_table(csv_files)
            stats_widget.setMinimumWidth(450)  # MPPT table: 4 columns, ~450px optimal
            stats_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        else:
            stats_widget = StatsTableFactory.create_scan_stats_table(csv_files)
            stats_widget.setMinimumWidth(500)  # Scan table: 6 columns, ~500px optimal
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

    def _plot_mppt(self, ax, csv_files, plot_title, data_type="pce"):
        """
        Unified MPPT plotting method that can plot PCE, voltage, or current data.

        Args:
            ax: matplotlib axis object
            csv_files: list of CSV file paths
            plot_title: title for the plot
            data_type: "pce", "voltage", or "current" to specify what to plot
        """
        overall_min_time, overall_max_time, overall_max_value = None, None, None

        # Get a color cycle for different CSV files
        if len(csv_files) <= 10:
            color_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9][:len(csv_files)]
            colors = [plt.cm.tab10(i/9.0) for i in color_indices]
        else:
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

            # Calculate data based on type
            if data_type == "pce":
                cell_area = float(meta_data["Cell Area (mm^2)"])
                data = ((pixel_V * pixel_mA / 1000) / (0.1 * cell_area)) * 100
                y_label = "PCE [%]"
            elif data_type == "voltage":
                data = pixel_V
                y_label = "Voltage [V]"
            elif data_type == "current":
                cell_area = float(meta_data["Cell Area (mm^2)"])
                data = pixel_mA / (0.1 * cell_area)  # Convert to current density (mA/cm²)
                y_label = "Current Density [mA/cm²]"
            else:
                raise ValueError(f"Invalid data_type: {data_type}. Must be 'pce', 'voltage', or 'current'")

            # Sample data if necessary
            if len(time) > 5000:
                step = int(np.ceil(len(time) / 5000))
                time = time[::step]
                data = data[::step, :]

            time = time / 60.0  # convert to minutes from seconds

            # Update overall ranges
            if overall_min_time is None:
                overall_min_time = min(time)
                overall_max_time = max(time)
                overall_max_value = np.max(data)
            else:
                overall_min_time = min(overall_min_time, min(time))
                overall_max_time = max(overall_max_time, max(time))
                overall_max_value = max(overall_max_value, np.max(data))

            # Convert time units if necessary
            if overall_max_time > 60:
                time /= 60.0
                overall_max_time /= 60
                time_label = "Time [hrs]"
            else:
                time_label = "Time [min]"

            # Plot each pixel
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

        ax.set_xlim(0, overall_max_time * 1.01)
        ax.set_ylim(0, overall_max_value * 1.15)
        ax.set_title(plot_title)
        ax.set_xlabel(time_label)
        ax.set_ylabel(y_label)
        ax.grid(True)

        # # Create line labels
        # self.line_label_texts = {}
        # lines = ax.get_lines()
        # if lines:
        #     x_min, x_max = ax.get_xlim()
        #     xvals = np.linspace(
        #         x_min + 0.1 * (x_max - x_min), x_max - 0.1 * (x_max - x_min), len(lines)
        #     )
        #     bold_font = FontProperties(weight="medium")
        #     label_texts = labelLines(
        #         lines,
        #         xvals=xvals,
        #         zorder=2.5,
        #         align=False,
        #         fontsize=11,
        #         fontproperties=bold_font,
        #     )
        #     self.line_label_texts = dict(zip(lines, label_texts))

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
                if ("Cell Area (mm^2)" in meta_data):
                    pixel_mA /= float(meta_data["Cell Area (mm^2)"])
                else:
                    pixel_mA /= 0.128
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

    def create_legend_widget(self, ax, mppt):
        """Creates a custom legend with checkboxes to toggle line visibility."""
        legend_widget = QWidget()
        legend_layout = QVBoxLayout(legend_widget)
        legend_layout.setContentsMargins(5, 5, 5, 5)

        # Three-way toggle for PCE, Voltage, Current (only if MPPT mode)
        if mppt:
            toggle_layout = QVBoxLayout()
            toggle_label = QLabel("Display Mode:")
            toggle_layout.addWidget(toggle_label)

            self.display_mode_group = QButtonGroup()

            self.pce_radio = QRadioButton("PCE")
            self.pce_radio.setChecked(True)  # Default selection
            self.pce_radio.toggled.connect(lambda checked: self.on_display_mode_changed("PCE", checked))
            self.display_mode_group.addButton(self.pce_radio)
            toggle_layout.addWidget(self.pce_radio)

            self.voltage_radio = QRadioButton("Voltage")
            self.voltage_radio.toggled.connect(lambda checked: self.on_display_mode_changed("Voltage", checked))
            self.display_mode_group.addButton(self.voltage_radio)
            toggle_layout.addWidget(self.voltage_radio)

            self.current_radio = QRadioButton("Current")
            self.current_radio.toggled.connect(lambda checked: self.on_display_mode_changed("Current", checked))
            self.display_mode_group.addButton(self.current_radio)
            toggle_layout.addWidget(self.current_radio)

            legend_layout.addLayout(toggle_layout)

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

    def on_display_mode_changed(self, mode, checked):
        """Handle display mode toggle changes (PCE, Voltage, Current)."""
        if checked and self.mppt and self.current_csv_files and self.current_ax:  # Only act when a radio button is selected, not deselected
            get_logger().log(f"Display mode changed to: {mode}")

            # Store current visibility states before clearing the plot
            visibility_states = self._store_line_visibility_states()

            # Clear the current plot
            self.current_ax.clear()

            # Plot based on selected mode
            if mode == "PCE":
                self._plot_mppt(self.current_ax, self.current_csv_files, self.current_plot_title, "pce")
            elif mode == "Voltage":
                self._plot_mppt(self.current_ax, self.current_csv_files, self.current_plot_title, "voltage")
            elif mode == "Current":
                self._plot_mppt(self.current_ax, self.current_csv_files, self.current_plot_title, "current")

            # Restore visibility states to the new plot
            self._restore_line_visibility_states(visibility_states)

            # Redraw the canvas
            if self.current_canvas:
                self.current_canvas.draw_idle()

            # Update the legend to reflect the new plot
            self._update_legend_for_current_plot()

    def _update_legend_for_current_plot(self):
        """Update the legend checkboxes to reflect the current plot state."""
        if not self.current_ax:
            return

        # Clear existing legend state
        self.legend_groups = {}
        self.legend_checkboxes = {}
        self.group_checkboxes = {}
        self.line_to_group = {}

        # Find the legend widget in the current layout and update it
        legend_widget = None
        for i in range(self.plot_container_layout.count()):
            widget_container = self.plot_container_layout.itemAt(i).widget()
            if widget_container:
                # Look for the splitter containing the legend
                splitter = widget_container.findChild(QSplitter)
                if splitter and splitter.count() > 0:
                    legend_widget = splitter.widget(0)  # Legend is the first widget in splitter
                    break

        if legend_widget:
            # Clear the existing legend content
            layout = legend_widget.layout()
            if layout:
                # Keep the toggle buttons but clear the scroll area content
                scroll_area = None
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item and item.widget() and isinstance(item.widget(), QScrollArea):
                        scroll_area = item.widget()
                        break

                if scroll_area:
                    # Recreate the legend content for the new plot
                    inner_widget = QWidget()
                    inner_layout = QVBoxLayout(inner_widget)
                    inner_layout.setContentsMargins(0, 0, 0, 0)

                    # Group lines by ID extracted from the label (same logic as create_legend_widget)
                    groups = {}
                    ungrouped = []
                    for line in self.current_ax.get_lines():
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

                    # Create checkboxes for each group
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

                        # Create indented checkboxes for each line in the group
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

                    # Add ungrouped lines
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

    def _store_line_visibility_states(self):
        """Store the current visibility state of all lines by their identifying characteristics."""
        visibility_states = {}

        if not self.current_ax:
            return visibility_states

        for line in self.current_ax.get_lines():
            label = line.get_label()
            # Create a unique identifier for each line based on pixel number and ID
            # Extract pixel number and ID from label like "Pixel 1 (ID 123)"
            pixel_match = re.search(r"Pixel (\d+)", label)
            id_match = re.search(r"\(ID (\d+)\)|ID(\d+)", label, re.IGNORECASE)

            if pixel_match:
                pixel_num = pixel_match.group(1)
                id_str = ""
                if id_match:
                    id_str = id_match.group(1) if id_match.group(1) is not None else id_match.group(2)

                # Create unique key: "pixel_number_id"
                key = f"pixel_{pixel_num}_id_{id_str}"
                visibility_states[key] = line.get_visible()

        return visibility_states

    def _restore_line_visibility_states(self, visibility_states):
        """Restore the visibility state of lines based on their identifying characteristics."""
        if not self.current_ax or not visibility_states:
            return

        for line in self.current_ax.get_lines():
            label = line.get_label()
            # Extract pixel number and ID from label
            pixel_match = re.search(r"Pixel (\d+)", label)
            id_match = re.search(r"\(ID (\d+)\)|ID(\d+)", label, re.IGNORECASE)

            if pixel_match:
                pixel_num = pixel_match.group(1)
                id_str = ""
                if id_match:
                    id_str = id_match.group(1) if id_match.group(1) is not None else id_match.group(2)

                # Create the same unique key used in storing
                key = f"pixel_{pixel_num}_id_{id_str}"

                # Restore visibility if we have a stored state for this line
                if key in visibility_states:
                    line.set_visible(visibility_states[key])
                    # Also update line label text visibility if it exists
                    if line in self.line_label_texts:
                        self.line_label_texts[line].set_visible(visibility_states[key])

