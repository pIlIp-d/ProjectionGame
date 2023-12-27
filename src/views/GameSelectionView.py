import math
import tkinter as tk
import platform

import cv2
from PIL import Image, ImageTk

from src.views.TkinterView import TkinterView


class GameSelectionView(TkinterView):
    def __init__(self, amount_of_games, cols=3, *args, **kwargs):
        super().__init__(title="Projection Game", *args, **kwargs)
        self._amount_of_games = amount_of_games
        self.cols = cols
        self.rows = math.ceil(self._amount_of_games / self.cols)
        self._button_grid: tk.Frame | None = None
        self.border_color = self.root.cget('bg')
        self.selected_border_color = "green"
        self.selected_game = 0
        self._scrollbar: tk.Scrollbar | None = None
        self._padding = 10
        self._images = [
            self.controller.get_startscreen_of_game(game_id)
            for game_id in range(self._amount_of_games)
        ]

    def _init_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True)
        # frame.columnconfigure(0, weight=3)
        # frame.columnconfigure(1, weight=1)
        # frame.rowconfigure(0, weight=1)
        # frame.rowconfigure(1, weight=1)
        self._add_button_sidebar(frame)
        self._add_game_grid(frame)
        return frame

    def _update_grid(self):
        canvas_width = max(1, self._canvas.winfo_width() - self._scrollbar.winfo_width())
        canvas_height = max(1, self._canvas.winfo_height())
        grid_item_width = canvas_width // self.cols - 2 * self._padding

        def resize_with_aspect_ratio(img):
            new_height = int(grid_item_width / 1.4)
            return cv2.resize(img, (grid_item_width, new_height))

        images = [ImageTk.PhotoImage(Image.fromarray(
            resize_with_aspect_ratio(image)
        )) for image in self._images]

        for i, button in enumerate(self._button_grid.children.values()):
            button.config(image=images[i])
            button.image = images[i]

        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"), height=self._button_grid.winfo_height())

        self.root.update()

    def _on_resize(self, event):
        self._update_grid()

    def _add_game_grid(self, parent):

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(parent, borderwidth=0, highlightthickness=0)
        frame_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Add a canvas in that frame
        self._canvas = tk.Canvas(frame_canvas, borderwidth=0, highlightthickness=0)
        self._canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=0, pady=0)

        # Link a scrollbar to the canvas
        self._scrollbar = tk.Scrollbar(frame_canvas, orient="vertical", command=self._canvas.yview)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.update_idletasks()

        self._canvas.configure(yscrollcommand=self._scrollbar.set)

        # Create a frame to contain the buttons
        self._button_grid = tk.Frame(self._canvas)
        self._button_grid.pack(side=tk.LEFT, fill=tk.BOTH, anchor="nw", expand=True, padx=0, pady=0)

        self._canvas.create_window((0, 0), window=self._button_grid, anchor='nw')

        self._canvas.bind("<Configure>", self._on_resize)

        buttons = []
        for i in range(len(self._images)):
            col = i % self.cols
            row = i // self.cols
            button = tk.Label(
                self._button_grid,
                relief="solid",
                borderwidth=2,
                highlightthickness=2,
                highlightbackground=self.border_color,
                highlightcolor=self.border_color
            )
            button.bind("<Enter>", lambda event, idx=i: self.on_hover_enter(idx))
            button.bind("<Leave>", lambda event, idx=i: self.on_hover_leave(idx))
            button.bind("<Button-1>", lambda event, idx=i: self.on_click(idx))

            button.grid(row=row, column=col, pady=self._padding, padx=self._padding)
            buttons.append(button)

        # Update buttons frames idle tasks to let tkinter calculate buttons sizes
        self._button_grid.update_idletasks()

        for i in range(self.cols):
            self._canvas.columnconfigure(i, weight=1)
        for i in range(self.rows):
            self._canvas.rowconfigure(i, weight=1)

        def on_scroll(event):
            # todo test on different platforms
            if platform.system() == 'Windows':
                self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif platform.system() == 'Darwin':
                self._canvas.yview_scroll(int(-1 * event.delta), "units")
            else:
                if event.num == 4:
                    self._canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self._canvas.yview_scroll(1, "units")

        self._button_grid.bind_all("<MouseWheel>", on_scroll)
        self.on_click(self.selected_game)
        self._update_grid()

    def _add_button_sidebar(self, parent):
        button_frame = tk.Frame(parent)
        button_frame.pack(side=tk.RIGHT)
        # button_frame.grid(row=1, column=1, padx=10, pady=10, sticky=tk.S)
        setup_button = tk.Button(button_frame, text="Setup",
                                 command=lambda: self.controller.start_setup())
        play_button = tk.Button(
            button_frame, text="Play Selected Game", command=lambda: self.controller.start_game(self.selected_game)
        )
        setup_button.pack(side=tk.BOTTOM)
        play_button.pack(side=tk.BOTTOM)
        # setup_button.grid(row=0, column=0, padx=10, pady=10, sticky=tk.SE)
        # play_button.grid(row=1, column=0, padx=10, pady=10, sticky=tk.SE)

    def _set_background_of_button(self, index, color):
        for i, key in enumerate(self._button_grid.children):
            if i == index:
                print(f"set {index} to {color}")
                self._button_grid.children[key].config(
                    highlightbackground=color,
                    highlightcolor=color
                )

    def on_hover_enter(self, index):
        self._set_background_of_button(index, self.selected_border_color)

    def on_hover_leave(self, index):
        if self.selected_game != index:
            self._set_background_of_button(index, self.border_color)

    def on_click(self, index):
        if self.selected_game is not None:
            # Reset the style of the previously selected item
            self._set_background_of_button(self.selected_game, self.border_color)

        # Update the selected item and its style
        self._set_background_of_button(index, self.selected_border_color)
        self.selected_game = index
