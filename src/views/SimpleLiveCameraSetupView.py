from abc import ABC

from src.views.SetupView import SetupView


class SimpleLiveCameraSetupView(SetupView, ABC):
    def _update(self, delta_time):
        if self._canvas is not None:
            img = self.controller.get_current_frame(delta_time)
            self._add_image_to_canvas(self._canvas, img)
