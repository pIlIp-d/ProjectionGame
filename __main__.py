from ttkthemes import ThemedTk
import tkinter as tk
from tkinter import ttk

from threading import Thread

from src.controller.SetupController import SetupController
from src.game.player_controller.HandPoseEstimator import HandPoseEstimator
from src.game.player_controller.MovenetHumanPoseEstimator import MovenetHumanPoseEstimator
from src.models.Model import Model

# todo make it properly resizeable

# todo send width and height to game (from View) when it changes and in the beginning
#   width = self._active_frame.winfo_width()
#   height = self._active_frame.winfo_height()

# todo make _update so that it doesnt need to check any conditions and add delta_time directly into it as parameter

initable_classes = [
    MovenetHumanPoseEstimator
]


def main():
    root = ThemedTk(theme="breeze")

    model = Model()
    SetupController(model, root)

    def init():
        for c in initable_classes:
            c.init()

    # todo find a better way, this one produces lag
    Thread(target=init, daemon=True).start()

    # app = CameraSelectView(root)
    root.mainloop()


if __name__ == "__main__":
    main()
