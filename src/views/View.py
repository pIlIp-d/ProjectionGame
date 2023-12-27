from abc import ABC, abstractmethod


class View(ABC):
    @abstractmethod
    def hide(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def close_window(self):
        pass

    @abstractmethod
    def destroy_window(self):
        pass
