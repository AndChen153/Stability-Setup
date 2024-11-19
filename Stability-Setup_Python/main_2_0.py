import tkinter as tk
import threading
from datetime import datetime

from constants_1_0 import Mode, constants_gui
from data_visualization import data_show_1_0 as data_show
from controller import multithreader_1_0 as multi_arduino

class App:
    #TODO: create input for folder title
    #TODO: replace this app with https://www.pythonguis.com/pyside6/
    def __init__(self, root):
        today = datetime.now().strftime("%b-%d-%Y %H_%M_%S")
        folder_path = "./data/" + today + "/"
        self.controller = multi_arduino.controller(
            folder_path = folder_path,
            today = today)

        self.root = root
        self.root.title("Stability Setup")
        self.image_refs = []  # To keep references to images

        # Create the top frame for page selection buttons
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.num_pages = len(Mode)
        self.pages_list = list(Mode)

        # Create page selection buttons
        self.page_buttons = []
        for i in range(self.num_pages):
            button = tk.Button(
                self.top_frame,
                text=constants_gui["pages"][self.pages_list[i]],
                command=lambda i=i: self.show_page(i),
            )
            button.pack(side=tk.LEFT)
            self.page_buttons.append(button)

        # Create the container for pages
        self.pages = {}

        # Create the frames for each page
        for i in range(self.num_pages):
            page = tk.Frame(self.root)
            page_id = self.pages_list[i]
            num_params = len(constants_gui["params"][page_id])
            entries_list = []

            # Add input parameters with default values
            for j in range(num_params):
                label = tk.Label(page, text=constants_gui["params"][page_id][j])
                label.grid(row=j, column=0, padx=5, pady=5, sticky="e")
                entry = tk.Entry(page)
                entry.insert(0, constants_gui["defaults"][page_id][j])
                entry.grid(row=j, column=1, padx=5, pady=5)
                entries_list.append(entry)

            # Add the Run button
            run_button = tk.Button(
                page, text="Run", command=lambda i=i: self.run_page(i)
            )
            run_button.grid(row=6, column=0, columnspan=2, pady=10)

            status_label = tk.Label(page, text="")
            status_label.grid(row=7, column=0, columnspan=2, pady=5)

            # Store the page frame and entries in the pages dictionary
            self.pages[i] = {
                "frame": page,
                "entries": entries_list,
                "status_label": status_label,
                "run_button": run_button  # Store the Run button reference
            }

        # Show the first page (page 0) by default
        self.current_page = 0
        self.pages[self.current_page]["frame"].pack(fill=tk.BOTH, expand=True)

        # Update the button styles to indicate the current page
        self.update_button_styles()

    def show_page(self, page_number):
        # Hide the current page
        self.pages[self.current_page]["frame"].pack_forget()
        # Show the new page
        self.current_page = page_number
        self.pages[self.current_page]["frame"].pack(fill=tk.BOTH, expand=True)
        # Update the button styles
        self.update_button_styles()

    def update_button_styles(self):
        for i, button in enumerate(self.page_buttons):
            if i == self.current_page:
                button.config(relief=tk.SUNKEN, state=tk.DISABLED)
            else:
                button.config(relief=tk.RAISED, state=tk.NORMAL)

    def run_page(self, page_number):
        # Disable the Run button to prevent multiple clicks
        run_button = self.pages[page_number]["run_button"]
        run_button.config(state=tk.DISABLED)

        self.disable_page_buttons()

        # Update status label
        status_label = self.pages[page_number]["status_label"]
        status_label.config(
            text="Running " + constants_gui["pages"][self.pages_list[page_number]]
        )

        page_id = self.pages_list[page_number]

        # Retrieve parameter values
        entries = self.pages[page_number]["entries"]
        values = [entry.get() for entry in entries]

        # Start backend processing in a new thread
        thread = threading.Thread(
            target=self.backend_task,
            args=(page_number, page_id, values),
            daemon=True,  # Daemon thread will exit when the main program exits
        )
        thread.start()

    def backend_task(self, page_number, page_id, values):
        print(f"Running backend task for page_id={page_id} with values={values}")
        data_locations = self.controller.run(page_id, values)
        if data_locations:

            image_folder_locations = []

            # Process data into images
            if page_id == Mode.SCAN:
                for scan_filename in data_locations:
                    folder_location = data_show.show_scan_graphs_one_graph(scan_filename)
                    image_folder_locations.append(folder_location)
            elif page_id == Mode.PNO:
                for pno_filename in data_locations:
                    folder_location = data_show.show_pce_graphs(pno_filename)
                    image_folder_locations.append(folder_location)

            print("Image folder locations:", image_folder_locations)
            # Schedule GUI update with image folder locations
            self.root.after(0, self.update_after_backend, page_number, image_folder_locations)

        else:
            self.root.after(0, self.update_after_backend, page_number, error="No Arduino Connected")

    def update_after_backend(self, page_number, image_folder_locations=None, error=None):
        # Re-enable the Run button
        run_button = self.pages[page_number]["run_button"]
        run_button.config(state=tk.NORMAL)

        # Re-enable the page buttons
        self.update_button_styles()

        # Update status label
        status_label = self.pages[page_number]["status_label"]
        if error:
            status_label.config(text=f"Error: {error}")
            tk.messagebox.showerror("Error", error)
        else:
            status_label.config(
                text=constants_gui["pages"][self.pages_list[page_number]] + " Finished"
            )


    def disable_page_buttons(self):
    # Disable all page buttons
        for button in self.page_buttons:
            button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
