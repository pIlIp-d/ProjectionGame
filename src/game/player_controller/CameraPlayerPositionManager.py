from collections import deque
import numpy as np

from src.game.player_controller.HandPoseEstimator import HandPoseEstimator
from src.game.player_controller.MovenetHumanPoseEstimator import MovenetHumanPoseEstimator
from src.game.player_controller.PlayerPositionManager import PlayerPositionManager
from src.game.player_controller.SmoothingFilter import SmoothingFilter
from src.game.player_controller.FloorPosEstimator import FloorPosEstimator
from src.game.player_controller.HumanPoseEstimator import HumanPoseEstimator
from src.models.Model import Model


class CameraPlayerPositionManager(PlayerPositionManager):

    def __init__(self, model: Model):
        super().__init__()
        self.model = model

        self._human_pose_estimator = MovenetHumanPoseEstimator()
        self._floor_pos_estimator = FloorPosEstimator(np.array(model.projector_edges))
        # todo fix edges to be in scale with the feet/make the projection_edges in range 0..1
        self.dimensions = self.model.camera.get_image().shape

        self._smoothness_threshold = 10
        self._last_positions = None

        self._position_smoother = [SmoothingFilter(3), SmoothingFilter(3), SmoothingFilter(3), SmoothingFilter(3)]
        self._counter = 0
        self._last_positions = []
        self._position_history = {}  # Dictionary to store position history for each player
        self.history_length = 5  # Number of frames to average over

    def _to_pixel(self, x, y):
        def limit_pixel(x, y):
            return [
                x if 0 <= x <= self.dimensions[1] else 0 if x < 0 else self.dimensions[1],
                y if 0 <= y <= self.dimensions[0] else 0 if y < 0 else self.dimensions[0]
            ]

        return limit_pixel(*[int(x * self.dimensions[1]), int(y * self.dimensions[0])])

    def _smooth_points(self, current_points: list):
        # smooth points by only updating point if it is further away from previous point than a certain threshold
        for i in range(min(len(current_points), len(self._last_positions))):
            for j in range(min(len(current_points[i]), len(self._last_positions[i]))):
                distance = np.linalg.norm(np.array(current_points[i][j]) - np.array(self._last_positions[i][j]))
                if distance > self._smoothness_threshold:
                    current_points[i].pop(j)
                else:
                    self._last_positions[i][j] = current_points[i][j]
        return current_points

    def get_players_positions(self):
        if self._counter % 1 == 0:
            frame = self.model.get_rgb_frame()
            players = self._human_pose_estimator.get_feet_position_from_image(frame)
            player_positions_2d = []

            for player_id, player in enumerate(players):
                feet_positions_2d = []
                for foot in player:
                    feet_positions_2d.append(
                        self._to_pixel(*self._floor_pos_estimator.get_point_on_floor(self._to_pixel(*foot)))
                    )

                if len(feet_positions_2d) > 0:
                    player_positions_2d.append(feet_positions_2d)

                    # smoothing of coords using history
                    if player_id not in self._position_history:
                        self._position_history[player_id] = deque(maxlen=self.history_length)
                    self._position_history[player_id].append(feet_positions_2d)
                    smoothed_position = np.mean(self._position_history[player_id], axis=0).tolist()
                    player_positions_2d[-1] = smoothed_position  # Update with smoothed position

            if player_positions_2d:
                self._last_positions = player_positions_2d

            # Update the position smoother for each foot
            for i, player in enumerate(player_positions_2d):
                if len(player) > 0:
                    self._position_smoother[i * 2].add_point(player[0])
                    self._position_smoother[i * 2 + 1].add_point(player[1])

        self._counter += 1
        return self._last_positions


"""
player:
    feet:
        x: int
        y: int
    non_visible_frames: int

if player_n.non_visible_frames > X:
    remove player_n
"""
