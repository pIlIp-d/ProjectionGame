import tkinter as tk
from tkinter import ttk

from src.views.SimpleLiveCameraSetupView import SimpleLiveCameraSetupView


class CameraSetupViewSimple(SimpleLiveCameraSetupView):
    def __init__(self, *args, **kwargs):
        super().__init__(prev_button_is_active=False, next_button_is_active=True, *args, **kwargs)

    def _add_menu(self, menu_frame):
        container_frame = tk.Frame(menu_frame)
        container_frame.pack(side=tk.TOP)
        camera_label = tk.Label(container_frame, text="Select Camera:")
        camera_label.pack(side=tk.LEFT)
        # camera_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)

        def get_camera_name(i):
            return f"Camera {i}"

        current_cam, cameras = self.controller.get_cameras()
        cameras_names = [get_camera_name(i) for i in cameras]

        if len(cameras) <= 0:
            raise ValueError("No camera connected.")
        elif current_cam < 0:
            current_cam = cameras[0]
            self.controller.set_camera(current_cam)

        selected_camera = tk.StringVar(container_frame, value=get_camera_name(current_cam))
        camera_option_menu = ttk.OptionMenu(
            container_frame,
            selected_camera,
            get_camera_name(current_cam),
            *cameras_names,
            **{"command": lambda x: self.controller.set_camera(x.split()[-1])}
        )
        camera_option_menu.pack(side=tk.RIGHT)
        # camera_option_menu.grid(row=0, column=2, padx=10, pady=10, sticky=tk.N)
