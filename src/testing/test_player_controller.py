from ..game.player_controller.HandPoseEstimator import HandPoseEstimator
from ..models.Model import Model
from ..game.player_controller.FloorPosEstimator import FloorPosEstimator
import numpy as np


class TestingManager:
    def __init__(self):
        self.model = Model()
        self.model.camera_source = 0
        print("loaded model")
        HandPoseEstimator.init()
        self._human_pose_estimator = HandPoseEstimator()
        # MovenetHumanPoseEstimator.init()
        # self._human_pose_estimator = MovenetHumanPoseEstimator()
        print("loaded handposeestimator")
        self._floor_pos_estimator = FloorPosEstimator(np.array(self.model.projector_edges))
        print("init floorestimator")

        self.dimensions = self.model.camera.get_image().shape
        print("init complete")

    def _to_pixel(self, x, y):
        def limit_pixel(x, y):
            return [
                x if 0 <= x <= self.dimensions[1] else 0 if x < 0 else self.dimensions[1],
                y if 0 <= y <= self.dimensions[0] else 0 if y < 0 else self.dimensions[0]
            ]

        return limit_pixel(*[int(x * self.dimensions[1]), int(y * self.dimensions[0])])

    def get_players_positions(self):
        frame = self.model.get_rgb_frame()
        players = self._human_pose_estimator.get_feet_position_from_image(frame)
        player_positions_2d = []
        for player in players:
            feet_positions_2d = []
            for foot in player:
                feet_positions_2d.append(
                    self._to_pixel(*self._floor_pos_estimator.get_point_on_floor(self._to_pixel(*foot)))
                )
            if len(feet_positions_2d) > 0:
                player_positions_2d.append(feet_positions_2d)

        return player_positions_2d
