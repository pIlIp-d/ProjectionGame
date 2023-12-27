import cv2
import numpy as np

from src.game.Game import Game


class EmptyGame(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    @classmethod
    def get_start_screen(cls, optional_text=""):
        return cls.create_image_with_text(optional_text)

    def get_next_frame(self, delta_time):
        self.counter += 1
        players = self._player_position_manager.get_players_positions()
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255)]
        image = np.zeros(self._player_position_manager.dimensions, dtype=np.uint8)
        for i, player in enumerate(players):
            for foot in player:
                x, y = foot
                cv2.circle(image, (int(x), int(y)), radius=25, color=colors[i % len(colors)], thickness=-1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        font_color = (255, 255, 255)  # white color in BGR format

        # Determine the position to place the text
        text_position = (50, 200)

        # Add text to the image
        seconds = delta_time.total_seconds()

        cv2.putText(image, "0" if seconds == 0 else str(int(1 / seconds)),
                    text_position, font, font_scale, font_color, font_thickness)

        return image
