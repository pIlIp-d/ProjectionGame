from enum import Enum


class Views(Enum):
    CAMERA_SETUP_VIEW = 0
    HARDWARE_SETUP_VIEW = 1
    PLAYING_FIELD_SETUP_VIEW = 2
    GAME_SELECTION_VIEW = 3
    GAME_VIEW = 4

    @classmethod
    def get(cls, index):
        return list(cls)[index]