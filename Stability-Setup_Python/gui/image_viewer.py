import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

class ImageViewer:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]

        if not self.image_files:
            messagebox.showerror("Error", "No image files found in the selected folder.")
            return

        # Determine max image width and set window dimensions
        max_width = 0
        max_height = 0
        for img_file in self.image_files:
            image_path = os.path.join(self.folder_path, img_file)
            image = Image.open(image_path)
            max_width = max(max_width, image.size[0])
            max_height = max(max_height, image.size[1])

        self.root = tk.Toplevel()
        self.root.title("Image Viewer")

        # Set window size based on the largest image dimensions
        self.root.geometry(f"{min(max_width, 810)}x{min(2 * max_height, 800)}")

        self.canvas = tk.Canvas(self.root)
        self.scroll_y = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_x = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.frame = tk.Frame(self.canvas)

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.image_refs = []
        self.display_images()

        # Bind mouse scroll for smooth scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)  # Windows & macOS
        self.canvas.bind_all("<Button-4>", self.on_mouse_wheel)  # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self.on_mouse_wheel)  # Linux (scroll down)

    def display_images(self):
        for img_file in self.image_files:
            image_path = os.path.join(self.folder_path, img_file)
            image = Image.open(image_path)
            image.thumbnail((800, 600))
            tk_image = ImageTk.PhotoImage(image)

            label = tk.Label(self.frame, image=tk_image)
            label.image = tk_image  # Keep a reference to prevent garbage collection
            label.pack(pady=5)
            self.image_refs.append(tk_image)

    def on_mouse_wheel(self, event):
        if event.num == 4 or event.delta > 0:  # Scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.canvas.yview_scroll(1, "units")

def run_image_viewer(folder_path):
    ImageViewer(folder_path)
