import os
from abc import abstractmethod

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class HumanPoseEstimator:
    @abstractmethod
    def get_feet_position_from_image(self, image):
        pass
