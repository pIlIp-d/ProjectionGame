from abc import abstractmethod


class HumanPoseEstimator:
    @abstractmethod
    def get_feet_position_from_image(self, image):
        pass
