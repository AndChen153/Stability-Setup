from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
import threading
import os
import glob

from src_python.constants_1_0 import Page, constants
from src_python.gui.resized_image_1_0 import ResizableImage
from src_python.data_visualization import data_show_1_0 as data_show
import src_python.controller.multithreader_1_0 as backend


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Stability Setup")
        self.image_refs = []  # To keep references to images

        # Create the top frame for page selection buttons
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.num_pages = len(Page)
        self.pages_list = list(Page)

        # Create page selection buttons
        self.page_buttons = []
        for i in range(self.num_pages):
            button = tk.Button(
                self.top_frame,
                text=constants["pages"][self.pages_list[i]],
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
            num_params = len(constants["params"][page_id])
            entries_list = []

            # Add input parameters with default values
            for j in range(num_params):
                label = tk.Label(page, text=constants["params"][page_id][j])
                label.grid(row=j, column=0, padx=5, pady=5, sticky="e")
                entry = tk.Entry(page)
                entry.insert(0, constants["defaults"][page_id][j])
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
            text="Running " + constants["pages"][self.pages_list[page_number]]
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
        data_locations = backend.run(page_id, values)
        image_folder_locations = []

        # Process data into images
        if page_id == Page.SCAN:
            for scan_filename in data_locations:
                folder_location = data_show.show_scan_graphs(
                    scan_filename,
                    show_dead_pixels=True,
                    pixels=None,
                    devices=None,
                    fixed_window=False,
                )
                image_folder_locations.append(folder_location)
        elif page_id == Page.PNO:
            for pno_filename in data_locations:
                folder_location = data_show.show_pce_graphs(pno_filename)
                image_folder_locations.append(folder_location)

        print("Image folder locations:", image_folder_locations)
        # Schedule GUI update with image folder locations
        self.root.after(0, self.update_after_backend, page_number, image_folder_locations)


    # def backend_task(self, page_number, page_id, values):
    #     # Simulate a time-consuming backend process
    #     try:
    #         print(page_id, values)
    #         data_locations = backend.run(page_id, values)
    #         image_folder_locations = []

    #         # process data into images
    #         if page_id == Page.SCAN:
    #             for scan_filename in data_locations:
    #                 image_folder_locations.append(
    #                     data_show.show_scan_graphs(
    #                         scan_filename,
    #                         show_dead_pixels=True,
    #                         pixels=None,
    #                         devices=None,
    #                         fixed_window=False,
    #                     )
    #                 )
    #         elif page_id == Page.PNO:
    #             for pno_filename in data_locations:
    #                 image_folder_locations.append(data_show.show_pce_graphs(pno_filename))

    #     except Exception as e:
    #         # Schedule GUI update with error
    #         print(str(e))
    #         self.root.after(0, self.update_after_backend, page_number, None, str(e))
    #     else:
    #         # Schedule GUI update with image file
    #         self.root.after(0, self.update_after_backend, page_number, image_folder_locations)
    #     # print(page_id, values)

    #     # # After processing, update the GUI (must be done in the main thread)
    #     # self.root.after(0, self.update_after_backend, page_number)


    def update_after_backend(self, page_number, image_folder_locations=None, error=None):
        print(f"update_after_backend called with page_number={page_number}, "
            f"image_folder_locations={image_folder_locations}, error={error}")

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
                text=constants["pages"][self.pages_list[page_number]] + " Finished"
            )
            if image_folder_locations:
                for location in image_folder_locations:
                    print(f"Showing images from: {location}")
                    self.show_images(location)


    # def update_after_backend(self, page_number, image_folder_locations=None, error=None):
    #     # Re-enable the Run button
    #     run_button = self.pages[page_number]["run_button"]
    #     run_button.config(state=tk.NORMAL)
    #     # Re-enable the page buttons
    #     self.update_button_styles()

    #     # Update status label
    #     status_label = self.pages[page_number]["status_label"]
    #     if error:
    #         status_label.config(text=f"Error: {error}")
    #     else:
    #         status_label.config(
    #             text=constants["pages"][self.pages_list[page_number]] + " Finished"
    #         )
    #         if image_folder_locations:
    #             for location in image_folder_locations:
    #                 self.show_images(location)

    def disable_page_buttons(self):
    # Disable all page buttons
        for i, button in enumerate(self.page_buttons):
            button.config(state=tk.DISABLED)

    def show_images(self, directory):
        # Get all image files in the directory
        image_files = self.get_all_images(directory)

        if not image_files:
            messagebox.showinfo("No Images Found", "No image files were found in the directory.")
            return

        # Create a new window to display images
        images_window = tk.Toplevel(self.root)
        images_window.title("Images Display")
        images_window.geometry("850x800")  # Set the default size to 800x600 pixels

        # Create a canvas with scrollbar
        canvas = tk.Canvas(images_window)
        scrollbar = tk.Scrollbar(images_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Clear image references
        self.image_refs.clear()

        for image_file in image_files:
            try:
                image = Image.open(image_file)
                # Optionally resize the image
                image.thumbnail((800, 800), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(image)
            except Exception as e:
                continue  # Skip files that cannot be opened as images

            label = tk.Label(scrollable_frame, image=photo)
            label.pack(padx=5, pady=5)
            self.image_refs.append(photo)  # Keep a reference


    def get_all_images(self, directory):
        # Initialize an empty list to store image file paths
        image_files = []

        # Iterate over each extension and find matching files
        image_files.extend(glob.glob(os.path.join(directory, "*.png")))

        return image_files


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
