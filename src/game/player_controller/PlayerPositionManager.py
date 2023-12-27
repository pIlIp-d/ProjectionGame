from abc import abstractmethod


class PlayerPositionManager:
    @abstractmethod
    def get_players_positions(self) -> list[list[int, int]]:
        pass
