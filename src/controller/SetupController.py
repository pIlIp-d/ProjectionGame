import math

import numpy as np

from src.game.EmptyGame import EmptyGame
from src.models.Model import Model
from src.views.CameraSetupView import CameraSetupViewSimple
from src.views.GameSelectionView import GameSelectionView
from src.views.GameView import GameView
from src.views.HardwareSetupView import HardwareSetupViewSimple
from src.views.PlayingFieldSetupView import PlayingFieldSetupView
from src.models.Views import Views


class SetupController:
    def __init__(self, model: Model, root):
        self.model = model
        self.root = root
        self.current_view = None

        self._current_game = None
        self.games = [
            (EmptyGame, "DrawInstallation"),
            (EmptyGame, "Pong"),
            (EmptyGame, "IceHockey"),
            (EmptyGame, "Lasers"),
            (EmptyGame, "Mini-golf"),
            (EmptyGame, "Bowling"),
            (EmptyGame, "Billiard"),
            (EmptyGame, "Fruit Ninja"),
            (EmptyGame, "Space Invaders")
        ]
        self.views = [
            CameraSetupViewSimple(root=self.root, controller=self),
            HardwareSetupViewSimple(root=self.root, controller=self),
            PlayingFieldSetupView(root=self.root, controller=self),
            GameSelectionView(root=self.root, controller=self, amount_of_games=len(self.games)),
            GameView(root=self.root, controller=self)
        ]
        self.start_setup()

    def start_setup(self):
        print("Controller.start_setup()")
        self.set_view(Views.CAMERA_SETUP_VIEW)

    def show_game_selection(self):
        print("Controller.show_selection()")
        self.set_view(Views.GAME_SELECTION_VIEW)

    def get_projector_edges(self):
        return self.model.projector_edges

    def next_view(self):
        print("next")
        self.set_view(Views((self.current_view.value + 1) % len(Views)))

    def prev_view(self):
        print("prev")
        self.set_view(Views((self.current_view.value - 1) % len(Views)))

    def update_projection_edges(self, x, y):
        mouse_pos = [x, y]
        current_edges = self.get_projector_edges()

        current_edges.sort(key=lambda point: np.linalg.norm(np.array(point) - np.array(mouse_pos)))
        # move the closest point to the mouse
        current_edges[0] = mouse_pos

        # resort the points to avoid the line between them to cross
        # for that it sorts by the angle to the center of the 4 points
        center_point = [int(sum([x[0] for x in current_edges]) / len(current_edges)),
                        int(sum([y[1] for y in current_edges]) / len(current_edges))]

        def get_angle(a, b):
            return math.atan2(a[1] - b[1], a[0] - b[0])

        self.model.projector_edges = sorted(current_edges, key=lambda point: get_angle(point, center_point))

    def set_view(self, view: Views):
        if self.current_view is not None:
            self.views[self.current_view.value].hide()
        self.model.save_config()
        if len(self.views) <= view.value:
            raise ValueError(f"View not found: {view}.")
        self.current_view = view
        self.views[self.current_view.value].show()

    def set_camera(self, new_camera):
        print("neu:", new_camera)
        self.model.camera_source = int(new_camera)

    def get_cameras(self) -> tuple[int, list]:
        return self.model.get_cameras()

    def start_game(self, i):
        if self._current_game is not None:
            self._current_game.stop_game()
        # instantiate chosen game
        self._current_game = self.games[i][0](self.games[i][1], self.model)
        print("game:", self._current_game)
        self.set_view(Views.GAME_VIEW)

    def close_window(self):
        for view in self.views:
            view.destroy_window()
        self.views[self.current_view.value].root.destroy()

    def get_startscreen_of_game(self, i):
        return self.games[i][0].get_start_screen(self.games[i][1])

    def get_current_frame(self, delta_time):
        if self.current_view == Views.GAME_VIEW:
            return self._current_game.get_next_frame(delta_time)
        else:
            # get frame from camera
            return self.model.get_rgb_frame()
