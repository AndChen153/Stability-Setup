# main.py
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import threading
from datetime import datetime
from helper.global_helpers import custom_print
from constants import Mode, ConstantsGUI
from data_visualization import data_plotter as data_plotter
from gui.image_viewer import ImageViewer
from controller.multi_arduino_controller import multi_controller

REMOVE_STOP_MODE = 1

class App:
    # TODO: create input for folder title
    # TODO: replace this app with https://www.pythonguis.com/pyside6/
    def __init__(self, root):
        self.today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        self.folder_path = None
        self.multi_controller = None
        self.trial_name_var = tk.StringVar(value="")

        self.root = root
        self.root.title("Stability Setup")
        self.image_refs = []

        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.num_pages = len(Mode) - REMOVE_STOP_MODE
        self.pages_list = list(Mode)[REMOVE_STOP_MODE:]

        self.image_viewer_path = None

        self.page_buttons = []
        for i in range(self.num_pages):
            button = tk.Button(
                self.top_frame,
                text=ConstantsGUI.pages[self.pages_list[i]],
                command=lambda i=i: self.show_page(i),
            )
            button.pack(side=tk.LEFT)
            self.page_buttons.append(button)

        self.pages = {}
        self.stop_events = {i: threading.Event() for i in range(self.num_pages)}
        self.threads = {i: None for i in range(self.num_pages)}

        for i in range(self.num_pages):
            page = tk.Frame(self.root)
            page_id = self.pages_list[i]
            num_params = len(ConstantsGUI.params[page_id])
            entries_list = []

            for j in range(num_params):
                label = tk.Label(page, text=ConstantsGUI.params[page_id][j])
                label.grid(row=j, column=0, padx=5, pady=5, sticky="e")

                if page_id in [Mode.SCAN, Mode.MPPT] and j == 0:
                    if not self.trial_name_var.get():
                        self.trial_name_var.set(ConstantsGUI.defaults[page_id][j])
                    entry = tk.Entry(page, textvariable=self.trial_name_var)
                else:
                    entry = tk.Entry(page)
                    entry.insert(0, ConstantsGUI.defaults[page_id][j])
                entry.grid(row=j, column=1, padx=5, pady=5)

                entries_list.append(entry)

                # Add folder selection button for Plotter page
                if page_id == Mode.PLOTTER and j == 0:
                    select_folder_button = tk.Button(
                        page, text="Select Folder", command=lambda entry=entry: self.select_folder(entry)
                    )
                    select_folder_button.grid(row=j, column=2, padx=5, pady=5)

            run_button = tk.Button(
                page, text="Run", command=lambda i=i: self.run_page(i)
            )
            run_button.grid(row=6, column=0, columnspan=2, pady=10)

            stop_button = tk.Button(
                page,
                text="Stop",
                command=lambda i=i: self.stop_page(i),
                state=tk.DISABLED,
            )
            stop_button.grid(row=6, column=1, pady=10, padx=5)

            status_label = tk.Label(page, text="")
            status_label.grid(row=7, column=0, columnspan=2, pady=5)

            self.pages[i] = {
                "frame": page,
                "entries": entries_list,
                "status_label": status_label,
                "run_button": run_button,
                "stop_button": stop_button,
            }

        self.current_page = 0
        self.pages[self.current_page]["frame"].pack(fill=tk.BOTH, expand=True)
        self.re_enable_buttons()

    def select_folder(self, entry):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry.delete(0, tk.END)
            entry.insert(0, folder_selected)

    def show_page(self, page_number):
        self.pages[self.current_page]["frame"].pack_forget()
        self.current_page = page_number
        self.pages[self.current_page]["frame"].pack(fill=tk.BOTH, expand=True)
        self.re_enable_buttons()

    def re_enable_buttons(self):
        for i, button in enumerate(self.page_buttons):
            if i == self.current_page:
                button.config(relief=tk.SUNKEN, state=tk.DISABLED)
            else:
                button.config(relief=tk.RAISED, state=tk.NORMAL)

    def run_page(self, page_number):
        self.today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")

        # Disable the Run button to prevent multiple clicks
        run_button = self.pages[page_number]["run_button"]
        run_button.config(state=tk.DISABLED)

        # Enable the Stop button
        stop_button = self.pages[page_number]["stop_button"]
        stop_button.config(state=tk.NORMAL)

        self.disable_page_buttons()

        # Update status label
        status_label = self.pages[page_number]["status_label"]
        status_label.config(
            text="Running " + ConstantsGUI.pages[self.pages_list[page_number]]
        )

        self.animate_loading(page_number)

        page_id = self.pages_list[page_number]

        # Retrieve parameter values
        entries = self.pages[page_number]["entries"]
        values = [entry.get() for entry in entries]

        if page_id == Mode.PLOTTER:
            self.multi_controller = multi_controller(
                trial_name="",
                date=self.today,
                plot_location=values[0],
                plotting_mode=True)
            self.image_viewer_path = values[0]
        else:
            self.trial_name = values.pop(0)
            custom_print(f"Starting Trial [{self.trial_name}] with Parameters:{values}")

            self.multi_controller = multi_controller(
                trial_name=self.trial_name,
                date=self.today,
                plotting_mode=False)

        # Clear any previous stop event
        self.stop_events[page_number].clear()

        # Start backend processing in a new thread
        thread = threading.Thread(
            target=self.backend_task,
            args=(page_number, page_id, values),
            daemon=True,  # Daemon thread will exit when the main program exits
        )
        self.threads[page_number] = thread
        thread.start()

    def stop_page(self, page_number):
        try:
            # Set the stop event to signal the thread to stop
            self.stop_events[page_number].set()

            # Update status label
            status_label = self.pages[page_number]["status_label"]
            status_label.config(
                text="Stopping " + ConstantsGUI.pages[self.pages_list[page_number]]
            )

            # Disable the Stop button to prevent multiple clicks
            stop_button = self.pages[page_number]["stop_button"]
            stop_button.config(state=tk.DISABLED)

            # Call the controller's stop method
            self.multi_controller.run(Mode.STOP)
        except AttributeError:
            messagebox.showerror("Error", "Stop method not implemented in multi_controller.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop: {e}")

    def backend_task(self, page_number, page_id, values):
        try:
            custom_print(f"Running backend task for page_id={page_id} with values={values}")
            self.multi_controller.run(page_id, values)

            # Monitor the stop event
            while not self.stop_events[page_number].is_set() and self.multi_controller.active_threads:
                threading.Event().wait(0.1)  # Avoid busy waiting

            if self.stop_events[page_number].is_set():
                custom_print(f"Task for page_id={page_id} has been stopped.")
                self.root.after(
                    0,
                    self.update_after_backend,
                    {
                        "page_number": page_number,
                        "stopped": True,
                    },
                )
                return

            if self.multi_controller.get_valid():
                # Schedule GUI update with image folder locations
                self.root.after(
                    0,
                    self.update_after_backend,
                    {
                        "page_number": page_number,
                        "page_id": page_id,
                    },
                )
            else:
                error_string = 'Arduino Location Not Found. \nRun "Stability-Setup_Python\\controller\\arduino_assignment_1_0.py" to find correct USB locations.'
                self.root.after(
                    0,
                    self.update_after_backend,
                    {
                        "page_number": page_number,
                        "error": error_string,
                    },
                )
        except Exception as e:
            custom_print(f"Error in backend_task: {e}")
            self.root.after(
                0,
                self.update_after_backend,
                {
                    "page_number": page_number,
                    "error": str(e),
                },
            )

    def update_after_backend(self, params):
        page_number = params.get("page_number")
        page_id = params.get("page_id")
        stopped = params.get("stopped", False)
        error = params.get("error", None)

        if page_id == Mode.PLOTTER:
            ImageViewer(self.image_viewer_path)

        self.stop_events[page_number].set()
        # Re-enable the Run button
        run_button = self.pages[page_number]["run_button"]
        run_button.config(state=tk.NORMAL)

        # Re-enable the page buttons
        self.re_enable_buttons()

        # Update status label
        status_label = self.pages[page_number]["status_label"]

        if error:
            messagebox.showerror("Error", error)
            status_label.config(text="Please Restart Program")
            run_button.config(state=tk.DISABLED)
            self.disable_page_buttons()
        elif stopped:
            status_label.config(
                text=ConstantsGUI.pages[self.pages_list[page_number]] + " Stopped"
            )
        else:
            status_label.config(
                text=ConstantsGUI.pages[self.pages_list[page_number]] + " Finished"
            )

    def disable_page_buttons(self):
        # Disable all page buttons
        for button in self.page_buttons:
            button.config(state=tk.DISABLED)

    def animate_loading(self, page_number, count=0):
        """ Rotates a loading animation next to the status text. """
        if self.stop_events[page_number].is_set():
            return  # Stop animation when the page stops

        animation_frames = ["|", "/", "-", "\\"]
        frame = animation_frames[count % len(animation_frames)]

        status_label = self.pages[page_number]["status_label"]
        status_label.config(
            text=f"Running {ConstantsGUI.pages[self.pages_list[page_number]]} {frame}"
        )

        # Schedule next update
        self.root.after(200, self.animate_loading, page_number, count + 1)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
