
from src.views.TkinterView import TkinterView
import tkinter as tk


class GameView(TkinterView):
    def __init__(self, *args, **kwargs):
        super().__init__(title="Projection Game", close_action=self.stop_game, *args, **kwargs)
        self._canvas = None

    def _init_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(frame)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.root.update_idletasks()
        return frame

    def stop_game(self):
        self.controller.show_game_selection()

    def _update(self, delta_time):
        if self._canvas is not None:
            rgb_image = self.controller.get_current_frame(delta_time)
            self._add_image_to_canvas(self._canvas, rgb_image)
