from time import sleep

import cv2
import numpy as np

from src.game.Initiated import Initiated
from src.game.player_controller.HumanPoseEstimator import HumanPoseEstimator

import tensorflow as tf
from ai_edge_litert.interpreter import Interpreter


class MovenetHumanPoseEstimator(HumanPoseEstimator, Initiated):
    _model = None

    @classmethod
    def init(cls):
        cls._model = Interpreter(
            model_path="models/movenet-lighting-float16/movenet-tflite-multipose-float16-v1.tflite")
        # cls._model.allocate_tensors()
        # cls._model = tf.saved_model.load("models/movenet-multipose-lightning/")

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

    def _detect(self, input_tensor):
        """Runs detection on an input image.

        Args:
            input_tensor: A [1, input_height, input_width, 3] Tensor of type tf.float32.
            input_size is specified when converting the model to TFLite.

        Returns:
            A tensor of shape [1, 6, 56].
        """

        input_details = self._model.get_input_details()
        output_details = self._model.get_output_details()

        is_dynamic_shape_model = input_details[0]['shape_signature'][2] == -1
        if is_dynamic_shape_model:
            input_tensor_index = input_details[0]['index']
            input_shape = input_tensor.shape
            self._model.resize_tensor_input(
                input_tensor_index, input_shape, strict=True)
        self._model.allocate_tensors()

        self._model.set_tensor(input_details[0]['index'], input_tensor.numpy())

        self._model.invoke()

        keypoints_with_scores = self._model.get_tensor(output_details[0]['index'])
        return keypoints_with_scores

    def _get_keypoints(self, image):
        # input_image = self._preprocess_image(image)
        # outputs = self._model.signatures["serving_default"](input_image)
        # keypoints = outputs['output_0'].numpy()
        # return keypoints
        # self._model.set_tensor(input_details[0]['index'], image)
        # self._model.invoke()
        # keypoints = self._model.get_tensor(output_details[0]['index'])
        # return keypoints
        image = self._preprocess_image(image)
        keypoints = self._detect(image)
        return keypoints

        keypoints = self._model.signatures['serving_default'](input_image)['output_0'].numpy()
        return keypoints

        # input_image = tf.image.resize_with_pad(tf.expand_dims(image, axis=0), 192, 192)
        # input_image = tf.cast(input_image, dtype=tf.int32)
        # self._model.set_tensor(input_details[0]['index'], input_image)

        # # Run inference
        # self._model.invoke()

        # # Get the output tensor
        # keypoints_with_scores = self._model.get_tensor(output_details[0]['index'])

        # # Reshape to get keypoints
        # keypoints = keypoints_with_scores.reshape((1, 1, 17, 3))  # Reshape if necessary

        # return keypoints[0][0]  # Return keypoints for the first person
        # return keypoints_with_scores = detect(self._model, tf.cast(image_tensor, dtype=tf.uint8))

        # keypoints_with_scores = results

        # # Extract keypoints and their confidence scores
        # keypoints = keypoints_with_scores[0][0][:, :2]  # Get x, y coordinates
        # scores = keypoints_with_scores[0][0][:, 2]      # Get confidence scores

        # return keypoints, scores

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
                # get_keypoint(15),  # left foot
                # get_keypoint(16)  # right foot
                get_keypoint(9),  # left hand
                get_keypoint(10)  # right hand
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
        input_size = 128
        input_image = cv2.resize(image, (input_size, input_size))
        input_image = input_image.reshape(-1, input_size, input_size, 3)
        input_image = tf.cast(input_image, dtype=tf.uint8)
        return input_image

    @staticmethod
    def _distance(p1, p2):
        return np.linalg.norm(np.array(p1[:2]) - np.array(p2[:2]))
