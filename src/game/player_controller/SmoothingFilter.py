import numpy as np


class SmoothingFilter:
    def __init__(self, smoothing_length):
        self._point_queue = np.zeros((smoothing_length, 2))
        self._current_index = 0

    def add_point(self, point):
        self._point_queue[self._current_index] = np.array(point)
        self._current_index = (self._current_index + 1) % len(self._point_queue)

    def get_smoothed_point(self):
        smoothed_point = [
            int(sum([p[0] for p in self._point_queue]) / len(self._point_queue)),
            int(sum([p[1] for p in self._point_queue]) / len(self._point_queue))
        ]
        return smoothed_point
