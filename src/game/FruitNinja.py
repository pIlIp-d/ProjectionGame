import queue
import cv2
import numpy as np

from src.game.Game import Game
import random
from time import sleep


class FruitNinja(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0
        self.image = None
        self._last_players = []
        self.fruits = []
        self._points = 0
        self._position_queue = queue.Queue()
        self.difficulty = 1

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
        self.image = np.zeros(self._player_position_manager.dimensions, dtype=np.uint8)

        height, width, _ = self.image.shape
        if self.counter % 1000 == 0:
            self.image = np.zeros(self._player_position_manager.dimensions, dtype=np.uint8)

        seconds = delta_time.total_seconds()
        targetFPS = 30
        targetFrameTime = 1 / targetFPS
        sleep_time = targetFrameTime - seconds
        if sleep_time > 0:
            sleep(sleep_time)  # Sleep to maintain target FPS

        players = self._player_position_manager.get_players_positions()

        # Update fruits
        if random.random() < self.difficulty/100:  # Control fruit spawn rate
            self.fruits.append(Fruit(width, height))

        # Draw and update fruits
        for fruit in self.fruits:
            fruit.fall()
            fruit.draw(self.image)

        sword_points = []
        # Draw current player positions and interpolate with last positions
        for i, player in enumerate(players):
            for j, point in enumerate(player):
                x, y = point
                # If there are previous positions to interpolate with
                if seconds < 3 and self._last_players and len(self._last_players) > i \
                        and len(self._last_players[i]) > j:
                    last_foot = self._last_players[i][j]

                    # Interpolate between current foot position and last foot position
                    num_points = 15  # Number of interpolated points
                    x_interp = np.linspace(last_foot[0], x, num_points)
                    y_interp = np.linspace(last_foot[1], y, num_points)
                    # Draw interpolated points
                    for k in range(num_points):
                        cv2.circle(self.image, (int(x_interp[k]), int(y_interp[k])),
                                   radius=SWORD_WIDTH, color=SWORD_COLOR, thickness=-1)
                        sword_points.append((int(x_interp[k]), int(y_interp[k])))
        # Check for slicing
        for fruit in self.fruits:
            if not fruit.is_sliced and fruit.y > height - fruit.radius:
                print("DIED")
            for point in sword_points:
                if np.linalg.norm(np.array(point) - np.array((fruit.x, fruit.y))) < fruit.radius:
                    fruit.is_sliced = True
                    self._points += 1

        # remove fruits
        self.fruits = [fruit for fruit in self.fruits if not fruit.is_sliced and fruit.y < height - fruit.radius]

        self.counter += 1
        if self.counter % 100 == 0:
            self.difficulty += 1

        self.image = cv2.flip(self.image, 1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        font_color = (255, 255, 255)  # white color in BGR format
        text_position = (20, 20)
        self.draw_text(self.image, str(self._points), font,
                       text_position, font_scale, font_thickness, font_color, (0, 0, 0))

        self._last_players = players.copy()  # Store current positions for next frame interpolation

        print("FRAMES", int(1 / seconds))
        return cv2.GaussianBlur(self.image, (3, 3), 0)

    def stop_game(self):
        pass


FRUIT_RADIUS_MIN = 20
FRUIT_RADIUS_MAX = 50
SWORD_WIDTH = 5
SWORD_COLOR = (0, 255, 0)
FRUIT_COLOR = (255, 0, 0)


class Fruit:
    def __init__(self, width, height):
        self.radius = random.randint(FRUIT_RADIUS_MIN, FRUIT_RADIUS_MAX)
        self.x = random.randint(self.radius, width - self.radius)
        self.y = 0  # Start from the top
        self.is_sliced = False

    def fall(self):
        self.y += 2  # Speed of falling

    def draw(self, image):
        if not self.is_sliced:
            cv2.circle(image, (self.x, self.y), self.radius, FRUIT_COLOR, -1)
