import cv2
import numpy as np

from src.game.Game import Game


class EmptyGame(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0
        self.image = None
        self._last_players = []
        self.fruits = []

    @classmethod
    def get_start_screen(cls, optional_text=""):
        return cls.create_image_with_text(optional_text)

    def draw_text(self, img, text,
                  font=cv2.FONT_HERSHEY_PLAIN,
                  pos=(0, 0),
                  font_scale=3,
                  font_thickness=2,
                  text_color=(0, 255, 0),
                  text_color_bg=(0, 0, 0)
                  ):

        x, y = pos
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_w, text_h = text_size
        cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
        cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

    def get_next_frame(self, delta_time):
        if self.counter % 1000 == 0:
            self.image = np.zeros(self._player_position_manager.dimensions, dtype=np.uint8)

        players = self._player_position_manager.get_players_positions()
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255)]

        seconds = delta_time.total_seconds()

        # Draw current player positions and interpolate with last positions
        for i, player in enumerate(players):
            for j, foot in enumerate(player):
                x, y = foot
                cv2.circle(self.image, (int(x), int(y)), radius=15, color=colors[i % len(colors)], thickness=-1)

                # If there are previous positions to interpolate with
                if seconds < 3 and self._last_players and len(self._last_players) > i \
                        and len(self._last_players[i]) > j:
                    last_foot = self._last_players[i][j]

                    # Interpolate between current foot position and last foot position
                    num_points = 10  # Number of interpolated points
                    x_interp = np.linspace(last_foot[0], x, num_points)
                    y_interp = np.linspace(last_foot[1], y, num_points)

                    # Draw interpolated points
                    for k in range(num_points):
                        cv2.circle(self.image, (int(x_interp[k]), int(y_interp[k])),
                                   radius=15, color=colors[i % len(colors)], thickness=-1)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        font_color = (255, 255, 255)  # white color in BGR format

        # Determine the position to place the text
        text_position = (50, 200)

        image = cv2.flip(self.image, 1)

        # Add text to the image
        # Uncomment the following line if you want to display FPS or similar information
        self.draw_text(image, "0" if seconds == 0 else str(int(1 / seconds)), font,
                       text_position, font_scale, font_thickness, font_color, (0, 0, 0))
        self.image = cv2.flip(self.image, 1)

        self.counter += 1
        self._last_players = players.copy()  # Store current positions for next frame interpolation
        return self.image
