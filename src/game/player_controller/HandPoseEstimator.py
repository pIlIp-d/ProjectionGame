from time import sleep

import cv2
import numpy as np

from src.game.Initiated import Initiated
from src.game.player_controller.HumanPoseEstimator import HumanPoseEstimator

import tensorflow as tf
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# @markdown We implemented some functions to visualize the hand landmark detection results. <br/> Run the following cell to activate the functions.

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image


class HandPoseEstimator(HumanPoseEstimator, Initiated):
    _model = None
    _options = None

    @classmethod
    def init(cls):
        VisionRunningMode = mp.tasks.vision.RunningMode
        baseOptions = mp.tasks.BaseOptions(model_asset_path='models/hand_landmarker/hand_landmarker.task')
        cls._options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=baseOptions,
            running_mode=VisionRunningMode.IMAGE
        )
        cls._model = mp.solutions.hands.Hands(
            static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5,
            model_complexity=0,  # 0 -> light model, 1 -> full model
        )
        mp_drawing = mp.solutions.drawing_utils

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
        if keypoints:

            persons = self._organize_hands_by_person(keypoints)
            return [[[x, y + self._y_offset] for (x, y) in person] for person in persons]
        else:
            return []

    def _get_keypoints(self, image):
        # input_image = self._preprocess_image(image)
        # input_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        # with self._model.create_from_options(self._options) as landmarker:
        #     hand_landmarker_result = landmarker.detect(input_image)
        #     print(hand_landmarker_result)
        #     annotated_image = draw_landmarks_on_image(input_image.numpy_view(), hand_landmarker_result)
        #     cv2.imwrite("test.png", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
        # raise ValueError("ENDING HERE")

        input_image = self._preprocess_image(image)
        input_image.flags.writeable = False
        results = self._model.process(input_image)
        return results.multi_hand_landmarks

        raise ValueError("END")
#        outputs = self._model.signatures["serving_default"](input_image)
#        keypoints = outputs['output_0'].numpy()
        return keypoints

    def _organize_hands_by_person(self, keypoints):
        # persons = []
        # default_hand = [[0, 0, 0], [0, 0, 0]]  # Default values for missing hand pairs

        # for person_keypoints in keypoints:
        #     hands = []

        #     # Extract hands from keypoints for this person
        #     index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

        #     for hand_keypoints in person_keypoints:
        #         if len(hand_keypoints) == 2:  # Expecting two keypoints for a hand
        #             hands.append(hand_keypoints)

        #     # Ensure we have exactly 4 hands for this person
        #     while len(hands) < 4:
        #         hands.append(default_hand)

        #     persons.append(hands)

        # # Optionally sort persons if needed based on any criteria
        # def sorted_persons():
        #     return sorted(persons, key=lambda person: sum(x for hand in person for (x, _, _) in hand) / len(person))

        # return sorted_persons()

        if keypoints:
            hand_centers = []
            for hand_landmarks in keypoints:

                index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                hand_centers.append((index_tip.x, index_tip.y))

            # Group hands based on proximity (max 2 per person)
            grouped_hands = []
            used_indices = set()

            def calculate_distance(hand_center1, hand_center2):
                return np.sqrt((hand_center1[0] - hand_center2[0]) ** 2 + (hand_center1[1] - hand_center2[1]) ** 2)

            while len(hand_centers) > 1:
                min_distance = float('inf')
                pair_indices = (-1, -1)

                # Find the closest pair of hands
                for i in range(len(hand_centers)):
                    for j in range(i + 1, len(hand_centers)):
                        distance = np.linalg.norm(np.array(hand_centers[i]) - np.array(hand_centers[j]))
                        if distance < min_distance:
                            min_distance = distance
                            pair_indices = (i, j)

                # Add the closest pair to grouped_hands and mark them as used
                person = []
                for i in pair_indices:
                    if i != -1:
                        person.append(hand_centers[i])
                if len(person) > 0:
                    grouped_hands.append(person)
                used_indices.update(pair_indices)
                # Remove used indices from hand_centers
                hand_centers.pop(max(pair_indices))  # Remove the larger index first
                hand_centers.pop(min(pair_indices))

            for hand in hand_centers:
                grouped_hands.append([hand, (0, 0)])
            return grouped_hands
        return []

    @staticmethod
    def _preprocess_image(image):
        #        input_image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
        input_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # input_image = input_image.reshape(-1, input_size, input_size, 3)
        # input_image = tf.cast(input_image, dtype=tf.int32)
        return input_image

    @staticmethod
    def _distance(p1, p2):
        return np.linalg.norm(np.array(p1[:2]) - np.array(p2[:2]))
