import tkinter as tk
from abc import abstractmethod

from src.views.TkinterView import TkinterView


# TODO add a reset config button

class SetupView(TkinterView):
    def __init__(self, prev_button_is_active: bool = True, next_button_is_active: bool = True, *args, **kwargs):
        super().__init__(title="Projection Game Setup", *args, **kwargs)
        self.prev_button_is_active = prev_button_is_active
        self.next_button_is_active = next_button_is_active
        self._canvas: tk.Canvas | None = None
        self._size = (720, 480)  # todo maybe get it from model
        self.root.geometry("x".join([str(x) for x in self._size]))

    def _init_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=tk.YES)
        # frame.columnconfigure(0, weight=3)
        # frame.columnconfigure(1, weight=1)
        # frame.columnconfigure(2, weight=1)
        # frame.rowconfigure(0, weight=1)
        # frame.rowconfigure(1, weight=1)
        self._add_canvas(frame)
        menu_frame = tk.Frame(frame)
        menu_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.YES, anchor="e")
        self._add_menu(menu_frame)
        self._add_progression_buttons(menu_frame, self.prev_button_is_active, self.next_button_is_active)
        return frame

    def _add_progression_buttons(self, menu_frame, prev_is_active: bool, next_is_active: bool):
        button_group = tk.Frame(menu_frame)
        button_group.pack(side=tk.BOTTOM, anchor="e")
        prev_button = tk.Button(
            button_group,
            text="Previous",
            state=tk.NORMAL if prev_is_active else tk.DISABLED,
            command=self.controller.prev_view
        )
        next_button = tk.Button(
            button_group,
            text="Next",
            state=tk.NORMAL if next_is_active else tk.DISABLED,
            command=self.controller.next_view
        )
        prev_button.pack(side=tk.LEFT)
        next_button.pack(side=tk.RIGHT)
        # prev_button.grid(row=1, column=1, padx=10, pady=10, sticky=tk.S)
        # next_button.grid(row=1, column=2, padx=10, pady=10, sticky=tk.S)

    def _add_canvas(self, setup_frame):
        self._canvas = tk.Canvas(setup_frame)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        # self._canvas.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

    @abstractmethod
    def _add_menu(self, setup_frame):
        pass
