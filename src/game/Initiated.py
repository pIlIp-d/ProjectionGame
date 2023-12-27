from abc import ABC, abstractmethod


class Initiated(ABC):

    @classmethod
    @abstractmethod
    def init(cls):
        pass
