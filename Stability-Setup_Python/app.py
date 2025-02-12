import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from constants import Mode, ConstantsGUI
from PySide6.QtCore import Qt, QFileSystemWatcher
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QSplitter,
    QSizePolicy,
)
# Import the QtAgg backend and Navigation Toolbar (compatible with PySide6)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stability Setup")
        self.setGeometry(100, 100, 1200, 600)

        # Left-side (Scan/MPPT) running state.
        self.running_left = False
        # Plotter running state (live updates will occur, but its Run button stays enabled).
        self.running_plotter = False

        # Dictionaries for buttons.
        self.run_buttons = {}
        self.stop_buttons = {}

        # Plotter attributes.
        self.data_location_line_edit = None
        self.plot_container = None
        self.plot_container_layout = None

        # File watcher for the CSV.
        self.csv_watcher = QFileSystemWatcher()
        self.csv_watcher.fileChanged.connect(self.on_csv_changed)

        # ------------------------------
        # Left Side: Tab Widget with Scan and MPPT pages.
        # ------------------------------
        self.left_tabs = QTabWidget()
        for mode, page_title in ConstantsGUI.pages.items():
            if mode == Mode.PLOTTER:
                continue  # Skip the Plotter page on the left.
            tab = QWidget()
            self.left_tabs.addTab(tab, page_title)
            self.setup_tab(mode, tab)

        # ------------------------------
        # Right Side: Plotter page (Mode.PLOTTER).
        # ------------------------------
        self.plotter_widget = QWidget()
        self.setup_tab(Mode.PLOTTER, self.plotter_widget)

        # ------------------------------
        # Create a horizontal splitter.
        # Left side (Scan/MPPT): 1/3 width, Right side (Plotter): 2/3 width.
        # ------------------------------
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_tabs)
        splitter.addWidget(self.plotter_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        self.setCentralWidget(splitter)

    def setup_tab(self, mode, widget):
        """
        Creates a form-based page.
        - For Mode.PLOTTER, a "CSV File" field with Browse button is added plus a Run button.
        - For other modes, a Run and a Stop button are added.
        """
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        if mode in ConstantsGUI.params:
            params = ConstantsGUI.params[mode]
            defaults = ConstantsGUI.defaults.get(mode, [""] * len(params))
            for param, default in zip(params, defaults):
                if mode == Mode.PLOTTER and param == "Data Location":
                    line_edit = QLineEdit()
                    line_edit.setText(default)
                    self.data_location_line_edit = line_edit
                    browse_button = QPushButton("Browse...")
                    browse_button.clicked.connect(lambda _, le=line_edit: self.open_file_dialog(le))
                    container = QWidget()
                    h_layout = QHBoxLayout(container)
                    h_layout.setContentsMargins(0, 0, 0, 0)
                    h_layout.addWidget(line_edit)
                    h_layout.addWidget(browse_button)
                    form_layout.addRow("CSV File", container)
                else:
                    line_edit = QLineEdit()
                    line_edit.setText(default)
                    form_layout.addRow(param, line_edit)
        else:
            form_layout.addRow(QLabel("No parameters defined for this mode."))

        # Button container.
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        run_button = QPushButton("Run")
        run_button.clicked.connect(lambda _, m=mode: self.run_action(m))
        button_layout.addWidget(run_button)
        self.run_buttons[mode] = run_button

        # Only left modes get a Stop button.
        if mode != Mode.PLOTTER:
            stop_button = QPushButton("Stop")
            stop_button.clicked.connect(lambda _, m=mode: self.stop_action(m))
            button_layout.addWidget(stop_button)
            self.stop_buttons[mode] = stop_button

        form_layout.addRow("", button_container)
        layout.addLayout(form_layout)

        # For the Plotter page, add an expanding container for the matplotlib plot.
        if mode == Mode.PLOTTER:
            self.plot_container = QWidget()
            self.plot_container_layout = QVBoxLayout(self.plot_container)
            self.plot_container_layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.plot_container, 1)

        widget.setLayout(layout)
        self.update_buttons()

    def update_buttons(self):
        """
        For left-side pages:
          - Disable the Run button when running.
          - Enable the Stop button only when running.
        The Plotter page's Run button is always enabled.
        """
        for mode in self.run_buttons:
            if mode == Mode.PLOTTER:
                self.run_buttons[mode].setEnabled(True)
            else:
                self.run_buttons[mode].setEnabled(not self.running_left)
        for mode in self.stop_buttons:
            self.stop_buttons[mode].setEnabled(self.running_left)

    def open_file_dialog(self, line_edit: QLineEdit):
        """
        Opens a file dialog to select a CSV file.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            line_edit.setText(file_path)

    def run_action(self, mode: Mode):
        """
        On Run:
          - For Mode.PLOTTER: load the CSV, update the plot, and add the file to the watcher.
          - For left modes: disable their Run button (and enable Stop) and trigger any additional functionality.
        """
        print(f"Run button clicked on page: {ConstantsGUI.pages.get(mode, 'Unknown')}")
        if mode == Mode.PLOTTER:
            self.running_plotter = True
            file_path = self.data_location_line_edit.text().strip()
            if os.path.isfile(file_path):
                self.update_plot_live()
                # Add the file to the watcher (if not already watching)
                if file_path not in self.csv_watcher.files():
                    self.csv_watcher.addPath(file_path)
            else:
                print("Invalid CSV file.")
        else:
            self.running_left = True
            self.update_buttons()
            # (Insert additional functionality for left-side modes here.)

    def stop_action(self, mode: Mode):
        """
        Stops the left-side functionality.
        """
        print(f"Stop button clicked on page: {ConstantsGUI.pages.get(mode, 'Unknown')}")
        self.running_left = False
        self.update_buttons()
        # (Insert additional stop functionality for left pages here.)

    def on_csv_changed(self, path):
        """
        Called when the CSV file changes.
        """
        print(f"CSV file changed: {path}")
        self.update_plot_live()

    def update_plot_live(self):
        """
        Loads the CSV file and updates the plot.
        Existing plot widgets are removed from the layout and replaced with new canvases.
        After creating the canvases, the figures are closed to avoid memory buildup.
        """
        file_path = self.data_location_line_edit.text().strip()
        if not os.path.isfile(file_path):
            print("Invalid CSV file.")
            return
        try:
            # -------------------------------
            # CSV Parsing and Data Extraction
            # -------------------------------
            arr = np.loadtxt(file_path, delimiter=",", dtype=str)
            plot_title = os.path.basename(file_path)[:-4] + '_Jmeas'

            headers = arr[6, :]
            header_dict = {value: index for index, value in enumerate(headers)}
            arr = arr[7:, :]
            data = arr[:, 2:-1]
            pixel_V = data[:, ::2].astype(float)    # even columns: voltage
            pixel_mA = data[:, 1::2].astype(float)    # odd columns: current (mA)
            pixel_mA /= 0.128

            # -------------------------------
            # Create Main Plot Figure (without legend)
            # -------------------------------
            fig, ax = plt.subplots()
            ax.set_title(plot_title)
            ax.set_xlabel('Bias [V]')
            ax.set_ylabel('Jmeas [mAcm-2]')
            jvLen = pixel_V.shape[0] // 2
            for i in range(pixel_V.shape[1]):
                # Plot Reverse series
                ax.plot(pixel_V[0:jvLen, i], pixel_mA[0:jvLen, i],
                        label=f"Pixel {i+1} Reverse")
                # Plot Forward series
                ax.plot(pixel_V[jvLen:, i], pixel_mA[jvLen:, i],
                        '--', label=f"Pixel {i+1} Forward")
            ax.grid(True)
            ax.spines['bottom'].set_position('zero')

            # -------------------------------
            # Create the legend figure
            # -------------------------------
            handles, labels = ax.get_legend_handles_labels()
            dummy_line = plt.Line2D([], [], linestyle='None')
            handles.append(dummy_line)
            labels.append("Reset Plot")
            fig_leg = plt.figure(figsize=(1, 1))
            ax_leg = fig_leg.gca()
            ax_leg.axis('off')
            leg = fig_leg.legend(handles, labels, loc='center', frameon=False)

            # Build mappings for interactive legend items.
            mapping = {}
            text_mapping = {}
            text_to_line = {}
            legend_lines = leg.get_lines()
            legend_texts = leg.get_texts()
            for i, (leg_line, leg_text) in enumerate(zip(legend_lines, legend_texts)):
                leg_line.set_picker(5)
                leg_text.set_picker(5)
                if labels[i] == "Reset Plot":
                    mapping[leg_line] = "all"
                else:
                    mapping[leg_line] = handles[i]
                text_mapping[leg_line] = leg_text
                text_to_line[leg_text] = leg_line

            def on_pick(event):
                picked_artist = event.artist
                if picked_artist not in mapping and picked_artist in text_to_line:
                    picked_artist = text_to_line[picked_artist]
                if picked_artist in mapping:
                    if mapping[picked_artist] == "all":
                        print("reset")
                        for leg_line, main_line in mapping.items():
                            if main_line != "all":
                                main_line.set_visible(True)
                                leg_line.set_alpha(1.0)
                                text_mapping[leg_line].set_color('black')
                    else:
                        orig_line = mapping[picked_artist]
                        if event.mouseevent.dblclick:
                            visible_lines = [line for line in mapping.values()
                                             if line != "all" and line.get_visible()]
                            if len(visible_lines) == 1 and orig_line.get_visible():
                                for leg_line, main_line in mapping.items():
                                    if main_line != "all":
                                        main_line.set_visible(True)
                                        leg_line.set_alpha(1.0)
                                        text_mapping[leg_line].set_color('black')
                            else:
                                for leg_line, main_line in mapping.items():
                                    if main_line == orig_line:
                                        main_line.set_visible(True)
                                        leg_line.set_alpha(1.0)
                                        text_mapping[leg_line].set_color('black')
                                    elif main_line != "all":
                                        main_line.set_visible(False)
                                        leg_line.set_alpha(0.2)
                                        text_mapping[leg_line].set_color('gray')
                        else:
                            visible = not orig_line.get_visible()
                            orig_line.set_visible(visible)
                            if visible:
                                picked_artist.set_alpha(1.0)
                                text_mapping[picked_artist].set_color('black')
                            else:
                                picked_artist.set_alpha(0.2)
                                text_mapping[picked_artist].set_color('gray')
                plot_canvas.draw_idle()
                legend_canvas.draw_idle()

            # -------------------------------
            # Build the canvases and layout
            # -------------------------------
            # Clear any existing widgets from the plot container.
            while self.plot_container_layout.count():
                item = self.plot_container_layout.takeAt(0)
                widget_item = item.widget()
                if widget_item is not None:
                    widget_item.deleteLater()

            plot_canvas = FigureCanvas(fig)
            plot_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            legend_canvas = FigureCanvas(fig_leg)
            legend_canvas.setFixedWidth(200)
            legend_canvas.mpl_connect('pick_event', on_pick)

            toolbar = NavigationToolbar(plot_canvas, self.plot_container)

            h_layout = QHBoxLayout()
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(plot_canvas, 1)
            h_layout.addWidget(legend_canvas)

            container = QWidget()
            container.setLayout(h_layout)

            v_layout = QVBoxLayout()
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.addWidget(toolbar)
            v_layout.addWidget(container, 1)

            widget_container = QWidget()
            widget_container.setLayout(v_layout)

            while self.plot_container_layout.count():
                item = self.plot_container_layout.takeAt(0)
                widget_item = item.widget()
                if widget_item is not None:
                    widget_item.deleteLater()
            self.plot_container_layout.addWidget(widget_container)

            plot_canvas.draw()
            legend_canvas.draw()

            # -------------------------------
            # Close the figures to free memory
            # -------------------------------
            plt.close(fig)
            plt.close(fig_leg)

        except Exception as e:
            print("Error updating CSV file:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
