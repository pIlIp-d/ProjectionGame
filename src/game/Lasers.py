import queue
import cv2
import numpy as np
import random
from time import sleep
import math

from src.game.Game import Game


# Constants for the Laser Avoid Game
LASER_SPEED = 2  # Speed at which lasers move
LASER_WIDTH = 3  # Width of the laser beam
LASER_WARNING_TIME = 1.0  # Seconds before laser appears
WARNING_COLOR = (0, 0, 255)  # Red color for warning
LASER_COLOR = (255, 0, 0)  # White color for the laser
PLAYER_RADIUS = 15  # Player's size
BACKGROUND_COLOR = (0, 0, 0)  # Black background


class LaserGame(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0
        self.image = None
        self.lasers = []
        self._points = 0
        self._position_queue = queue.Queue()
        self.difficulty = 10
        self._last_players = []

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

        seconds = delta_time.total_seconds()
        targetFPS = 30
        targetFrameTime = 1 / targetFPS
        players = self._player_position_manager.get_players_positions()

        sleep_time = targetFrameTime - seconds
        if sleep_time > 0:
            sleep(sleep_time)

        # Update lasers
        if random.random() < self.difficulty / 100:  # Control laser spawn rate
            self.spawn_laser(width, height)

        print(players)
        for player in players:
            print(player)
            for player_x, player_y in player:
                print(player_x, player_y)
                player_x, player_y = int(player_x), int(player_y)
                # Move lasers and check for collision with the player
                for laser in self.lasers:
                    laser.move()
                    laser.draw(self.image)
                    if laser.collides_with_player(player_x, player_y):
                        print("GAME OVER! Hit by a laser!")
                        self._points = 0
                        self.lasers = []
                        return self.image  # Return the image (Game Over)

                # Draw current player position
                cv2.circle(self.image, (player_x, player_y), PLAYER_RADIUS, (0, 255, 0), -1)

        self.image = cv2.flip(self.image, 1)

        # Draw the score
        self._points += 1
        self.draw_text(self.image, str(self._points // 10), font=cv2.FONT_HERSHEY_SIMPLEX, pos=(20, 20), font_scale=2)

        self.counter += 1
        if self.counter % 100 == 0:
            self.difficulty += 1

        return cv2.GaussianBlur(self.image, (3, 3), 0)

    def spawn_laser(self, width, height):
        # Randomly spawn a laser from the left or right side of the screen
        start_side = random.choice(['left', 'right'])
        start_x = 0 if start_side == 'left' else width
        start_y = random.randint(0, height)

        # Random direction and speed
        angle = random.uniform(-math.pi / 4, math.pi / 4)  # Random angle between -45 and 45 degrees
        laser = Laser(start_x, start_y, angle, LASER_SPEED, width, height)
        self.lasers.append(laser)

    def stop_game(self):
        pass


LASER_THICKNESS = 5


class Laser:
    def __init__(self, x, y, angle, speed, screen_width, screen_height):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self):
        # Move the laser along its path
        self.x += self.speed * np.cos(self.angle)
        self.y += self.speed * np.sin(self.angle)

    def draw(self, image):
        # Draw the laser as a line on the screen
        cv2.line(image, (int(self.x), int(self.y)),
                 (int(self.x + LASER_WIDTH * np.cos(self.angle)),
                  int(self.y + LASER_WIDTH * np.sin(self.angle))),
                 LASER_COLOR, LASER_THICKNESS)

    def collides_with_player(self, player_x, player_y):
        # Check if the laser intersects the player's position
        dist = np.linalg.norm(np.array([self.x, self.y]) - np.array([player_x, player_y]))
        return dist < PLAYER_RADIUS  # If the distance between laser and player is smaller than the player's radius
