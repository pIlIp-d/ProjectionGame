from time import sleep

import cv2
import numpy as np
from src.game.Initiated import Initiated
from src.game.player_controller.HumanPoseEstimator import HumanPoseEstimator
import mediapipe as mp

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)


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

        input_image = self._preprocess_image(image)
        input_image.flags.writeable = False
        results = self._model.process(input_image)
        return results.multi_hand_landmarks

    def _organize_hands_by_person(self, keypoints):
        if keypoints:
            hand_centers = []
            for hand_landmarks in keypoints:
                index_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
                hand_centers.append((index_tip.x, index_tip.y))

            # Group hands based on proximity (max 2 per person)
            grouped_hands = []
            used_indices = set()

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
        input_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return input_image

    @staticmethod
    def _distance(p1, p2):
        return np.linalg.norm(np.array(p1[:2]) - np.array(p2[:2]))
