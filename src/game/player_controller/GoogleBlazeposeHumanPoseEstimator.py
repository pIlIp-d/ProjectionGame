import os
from typing import Tuple, List

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from src.game.player_controller.HumanPoseEstimator import HumanPoseEstimator


class GoogleBlazeposeHumanPoseEstimator(HumanPoseEstimator):
    def __init__(self):
        super().__init__()
        base_options = python.BaseOptions(
            model_asset_path=os.path.join(os.path.dirname(__file__), "../../../pose_landmarker_lite.task"))
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True,
            min_pose_detection_confidence=0.3,
            min_pose_presence_confidence=0.3
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def get_feet_position_from_image(self, image):
        # To improve performance, optionally mark the image as not writeable to pass by reference.
        image.flags.writeable = False

        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

        # Detect pose landmarks from the input image.
        detection_result = self.detector.detect(image)

        if detection_result.pose_landmarks:
            left_foot_indices = [32, 28, 30]
            right_foot_indices = [27, 29, 31]

            left_foot_points = [detection_result.pose_landmarks[0][i] for i in left_foot_indices]
            right_foot_points = [detection_result.pose_landmarks[0][i] for i in right_foot_indices]

            # left_foot_world_points = [detection_result.pose_world_landmarks[0][i] for i in left_foot_indices]
            # right_foot_world_points = [detection_result.pose_world_landmarks[0][i] for i in right_foot_indices]

            def get_point_avg(points):
                return [sum([p.x for p in points]) / len(points), sum([p.y for p in points]) / len(points)]

            # todo clean up this function
            # todo add multi player support
            return get_point_avg(left_foot_points), get_point_avg(right_foot_points)
            # , get_point_avg(                left_foot_world_points), get_point_avg(right_foot_world_points)
        return None, None  # , None, None
