import tkinter as tk

import cv2
from PIL import Image, ImageTk

from src.views.SetupView import SetupView


class PlayingFieldSetupView(SetupView):

    def _add_menu(self, menu_frame):
        tutorial_text = tk.Label(menu_frame, text="""
            Use your mouse to set the points to the edges of the projected Image.
        """)
        tutorial_text.pack(side=tk.TOP)
        # tutorial_text.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)
        self._canvas.bind('<1>', self.click)

    def click(self, event):
        self.controller.update_projection_edges(event.x, event.y)
        # drag
        self._canvas.bind('<Motion>', lambda e: self.controller.update_projection_edges(e.x, e.y))

        # stop dragging when mouse is released
        self._canvas.bind('<ButtonRelease-1>', lambda _: self._canvas.unbind('<Motion>'))

    def _update(self, delta_time):
        if self._canvas is not None:
            rgb_image = self.controller.get_current_frame(delta_time)

            edges = self.controller.get_projector_edges()
            color = (255, 0, 0)
            for i, e in enumerate(edges):
                cv2.line(rgb_image, e, edges[(i + 1) % len(edges)], color, 2)
                cv2.circle(rgb_image, e, 10, color, -1)

            self._add_image_to_canvas(self._canvas, rgb_image)
