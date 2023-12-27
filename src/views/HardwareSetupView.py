import tkinter as tk

from src.views.SimpleLiveCameraSetupView import SimpleLiveCameraSetupView


class HardwareSetupViewSimple(SimpleLiveCameraSetupView):
    def _add_menu(self, menu_frame):
        tutorial_text = tk.Label(menu_frame, text="""
            Set up your camera and projector so that the playing field is
            projected and completely visible to the camera.

            Additionally check that the players heads and feet are visible at any
            point in the playing field
        """)
        tutorial_text.pack(side=tk.TOP)
        # tutorial_text.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)
