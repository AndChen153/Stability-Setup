import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
class ResizableImage(tk.Label):
    def __init__(self, parent, image_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.image_path = image_path
        self.original_image = Image.open(self.image_path)
        self.photo_image = None
        self.bind('<Configure>', self.resize_image)
        self.resize_image(None)  # Initial display

    def resize_image(self, event):
        if event:
            new_width = event.width
            new_height = event.height
        else:
            new_width = self.winfo_width()
            new_height = self.winfo_height()

        # Maintain aspect ratio
        width_ratio = new_width / self.original_image.width
        height_ratio = new_height / self.original_image.height
        ratio = min(width_ratio, height_ratio)
        resized_width = max(1, int(self.original_image.width * ratio))
        resized_height = max(1, int(self.original_image.height * ratio))

        resized_image = self.original_image.resize((resized_width, resized_height), Image.ANTIALIAS)
        self.photo_image = ImageTk.PhotoImage(resized_image)
        self.config(image=self.photo_image)