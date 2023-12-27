import tkinter as tk
from abc import abstractmethod
from datetime import datetime
from PIL import Image, ImageTk

from src.views.View import View


class TkinterView(View):
    def __init__(self, root, controller, title: str, close_action=None):
        self._is_active = False
        self.root = root
        self.controller = controller
        self.root.title(title)
        self._active_frame: tk.Frame | None = None
        self._last_time = datetime.now()

        if close_action is None:
            close_action = self.close_window
        self.close_action = close_action
        self._pack_info = None

    def hide(self):
        self._is_active = False
        if self._active_frame is None:
            self._active_frame = self._init_frame()
            self._pack_info = self._active_frame.pack_info()
        self._active_frame.pack_forget()

    def show(self):
        self._is_active = True
        if self._active_frame is None:
            self._active_frame = self._init_frame()
            self._pack_info = self._active_frame.pack_info()
        self.root.protocol("WM_DELETE_WINDOW", self.close_action)
        self._active_frame.pack(self._pack_info)
        self.__make_update()

    def close_window(self):
        self.controller.close_window()

    def destroy_window(self):
        if self._active_frame is not None:
            self._active_frame.destroy()

    @abstractmethod
    def _init_frame(self) -> tk.Frame:
        pass

    def __make_update(self):
        if self._is_active:
            current_time = datetime.now()
            delta_time = current_time - self._last_time
            self._last_time = current_time
            self._update(delta_time)
            self.root.after(10, lambda: self.__make_update())

    def _add_image_to_canvas(self, canvas, image: tk.PhotoImage, update=True):
        # Get the current size of the canvas
        canvas_width = max(1, canvas.winfo_width())
        canvas_height = max(1, canvas.winfo_height())

        image = Image.fromarray(image)

        initial_width, initial_height = image.size

        # Calculate the size for the image to fit the canvas while maintaining aspect ratio
        canvas_aspect_ratio = canvas_width / canvas_height
        image_aspect_ratio = initial_width / initial_height

        print(canvas_width, canvas_height, initial_width, initial_height)
        print(canvas_aspect_ratio, image_aspect_ratio)

        if canvas_aspect_ratio > image_aspect_ratio:
            new_width = max(int(canvas_height * image_aspect_ratio), 1)
            new_height = canvas_height
        else:
            new_width = canvas_width
            new_height = max(int(canvas_width / image_aspect_ratio), 1)

        # Resize the image
        resized_image = image.resize((new_width, new_height))

        # Calculate the position to center the image on the canvas
        x_position = (canvas_width - new_width) // 2
        y_position = (canvas_height - new_height) // 2

        # Add the image to the canvas
        tk_image = ImageTk.PhotoImage(resized_image)
        canvas.create_image(x_position, y_position, anchor=tk.NW, image=tk_image)
        canvas.image = tk_image

        if update:
            self.root.update()

    def _update(self, delta_time):
        pass
