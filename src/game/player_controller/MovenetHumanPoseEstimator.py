from time import sleep

import cv2
import numpy as np

from src.game.Initiated import Initiated
from src.game.player_controller.HumanPoseEstimator import HumanPoseEstimator

import tensorflow as tf


class MovenetHumanPoseEstimator(HumanPoseEstimator, Initiated):
    _model = None

    @classmethod
    def init(cls):
        cls._model = tf.saved_model.load("models/movenet-multipose-lightning/")

    def __init__(self, y_offset=0.1, confidence_threshold=0.2, distance_threshold=0.05):
        super().__init__()
        # maybe add a scale for y_offset in gui
        self._y_offset = y_offset
        self._confidence_threshold = confidence_threshold
        self._distance_threshold = distance_threshold
        while not self._model:
            sleep(1)  # Adjust the sleep duration as needed

    def get_feet_position_from_image(self, image):
        keypoints = self._get_keypoints(image)
        persons = self._organize_keypoints_by_person(keypoints)
        return [[[x, y + self._y_offset] for (x, y) in person] for person in persons]

    def _get_keypoints(self, image):
        input_image = self._preprocess_image(image)
        outputs = self._model.signatures["serving_default"](input_image)
        keypoints = outputs['output_0'].numpy()
        return keypoints

    def _organize_keypoints_by_person(self, keypoints):
        persons = []
        for person_keypoints in keypoints[0]:
            def get_keypoint(keypoint_id):
                return (
                    person_keypoints[3 * keypoint_id + 1],
                    person_keypoints[3 * keypoint_id],
                    person_keypoints[3 * keypoint_id + 2]
                )

            def already_in_persons(f):
                return any(
                    self._distance_threshold > self._distance(existing_foot, f[0])
                    for existing_person in persons for existing_foot in existing_person
                )

            feet = [
                get_keypoint(15),  # left foot
                get_keypoint(16)  # right foot
            ]

            if all([foot[2] > self._confidence_threshold for foot in feet]) and not already_in_persons(feet):
                persons.append(feet)

        def sorted_persons_from_left_to_right():
            def avg_for_x(l):
                return sum(x for x, _, _ in l) / len(l)

            return sorted(persons, key=lambda p: avg_for_x(p))

        return [[[x, y] for (x, y, _) in person]
                for person in sorted_persons_from_left_to_right()]

    @staticmethod
    def _preprocess_image(image):
        input_size = 256
        input_image = cv2.resize(image, (input_size, input_size))
        input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
        input_image = input_image.reshape(-1, input_size, input_size, 3)
        input_image = tf.cast(input_image, dtype=tf.int32)
        return input_image

    @staticmethod
    def _distance(p1, p2):
        return np.linalg.norm(np.array(p1[:2]) - np.array(p2[:2]))
