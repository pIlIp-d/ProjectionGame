from abc import abstractmethod

import cv2
import numpy as np

from src.game.player_controller.CameraPlayerPositionManager import CameraPlayerPositionManager


class Game:
    def __init__(self, name, model):
        self.name = name
        self._player_position_manager = CameraPlayerPositionManager(model)

    @classmethod
    @abstractmethod
    def get_start_screen(cls, optional_text=""):
        return None

    @abstractmethod
    def get_next_frame(self, delta_time):
        return None

    @staticmethod
    def create_image_with_text(text, border_size=10, font_size=1, font_thickness=2):
        # Set the font and other properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = font_size
        font_color = (255, 255, 0)
        line_type = cv2.LINE_AA

        # Calculate the text size to determine the image size
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        image_size = (text_size[0] + 2 * border_size, text_size[1] + 2 * border_size)

        # Create a black image
        image = np.zeros((image_size[1], image_size[0], 3), dtype=np.uint8)

        # Add a border to the image
        image = cv2.copyMakeBorder(
            image, border_size, border_size, border_size, border_size,
            cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
        # Calculate the position to center the text
        text_position = ((image.shape[1] - text_size[0]) // 2, (image.shape[0] + text_size[1]) // 2)

        # Put the text on the image
        cv2.putText(image, text, text_position, font, font_scale, font_color, font_thickness, line_type)

        return image
