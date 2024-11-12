import cv2

from src.models.Config import CameraConfig
from src.models.CameraFrame import CameraFrame


class Model:
    def __init__(self):
        self._camera_config = CameraConfig()
        self.camera: None | CameraFrame = None

    def save_config(self):
        self._camera_config.save_config()

    @property
    def camera_source(self):
        return self._camera_config.camera_name

    @camera_source.setter
    def camera_source(self, camera_name):
        self._camera_config.camera_name = camera_name
        if self.camera:
            self.camera.stop()
            del self.camera
        self.camera = CameraFrame(self.camera_source)

    @property
    def projector_edges(self):
        if self._camera_config.projector_edges is None:
            if self.camera is None:
                raise ValueError("Camera needs to be configured first!")
            camera_dimensions = self.camera.get_dimensions()
            return [[int(x), int(y)] for x, y in [
                # default edge positions
                [camera_dimensions[0] / 4, camera_dimensions[1] / 4],  # top left
                [camera_dimensions[0] * 2 / 4, camera_dimensions[1] / 4],  # top right
                [camera_dimensions[0] * 2 / 4, camera_dimensions[1] * 2 / 4],  # bottom right
                [camera_dimensions[0] / 4, camera_dimensions[1] * 2 / 4]  # bottom left
            ]]
        return self._camera_config.projector_edges

    @projector_edges.setter
    def projector_edges(self, edges):
        self._camera_config.projector_edges = edges

    def get_cameras(self) -> tuple[int, list]:
        cameras_available = []
        for camera_index in range(10):
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                cameras_available.append(camera_index)
                cap.release()

        # reset default value if camera not found
        if self.camera_source not in cameras_available:
            self.camera_source = -1
        return self.camera_source, cameras_available

    def get_rgb_frame(self):
        if self.camera is None:
            self.camera = CameraFrame(self.camera_source)
        return self.camera.get_image()

    def close(self):
        self.camera.stop()
