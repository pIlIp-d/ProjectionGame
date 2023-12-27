import cv2
import numpy as np


class FloorPosEstimator:
    def __init__(self, edge_points: np.array):
        floor_points = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
        self.homography_matrix, _ = cv2.findHomography(edge_points, floor_points)

    def get_point_on_floor(self, image_point):
        image_point = np.array(image_point, np.float32)
        floor_point = cv2.perspectiveTransform(
            image_point.reshape(-1, 1, 2), self.homography_matrix  # todo check if parameters are needed
        )
        return floor_point[0, 0]
