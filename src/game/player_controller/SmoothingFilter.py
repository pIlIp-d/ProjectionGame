from collections import deque
import numpy as np


class SmoothingFilter:
    def __init__(self, smoothing_length):
        #        self._point_queue = np.zeros((smoothing_length, 2))
        self._point_queue = deque(maxlen=smoothing_length)
        self._point_queue.append([0, 0])
        self._current_index = 0

    def add_point(self, point):
        self._point_queue.append(np.array(point))

    def get_smoothed_point(self):
        smoothed_point = [
            int(sum([p[0] for p in self._point_queue]) / len(self._point_queue)),
            int(sum([p[1] for p in self._point_queue]) / len(self._point_queue))
        ]
        return smoothed_point
