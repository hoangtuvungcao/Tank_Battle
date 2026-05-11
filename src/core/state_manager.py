from enum import Enum


class GameState(Enum):
    """Các trạng thái của game."""
    MENU = "menu"
    SETTINGS = "settings"
    TANK_SELECT = "tank_select"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_TRANSITION = "level_transition"


class StateManager:
    """Quản lý chuyển đổi trạng thái game."""

    _CHUYEN_DOI_HOP_LE = {
        GameState.MENU: {GameState.TANK_SELECT, GameState.SETTINGS},
        GameState.SETTINGS: {GameState.MENU},
        GameState.TANK_SELECT: {GameState.PLAYING, GameState.MENU},
        GameState.PLAYING: {GameState.PAUSED, GameState.GAME_OVER, GameState.LEVEL_TRANSITION},
        GameState.PAUSED: {GameState.PLAYING, GameState.MENU},
        GameState.GAME_OVER: {GameState.MENU},
        GameState.LEVEL_TRANSITION: {GameState.PLAYING},
    }

    def __init__(self, initial_state=GameState.MENU):
        self.current_state = initial_state
        self.previous_state = initial_state

    def change_state(self, new_state):
        allowed = self._CHUYEN_DOI_HOP_LE.get(self.current_state, set())
        if new_state in allowed:
            self.previous_state = self.current_state
            self.current_state = new_state
            return True
        return False

    def is_state(self, state):
        return self.current_state == state

    def go_back(self):
        if self.previous_state != self.current_state:
            temp = self.current_state
            self.current_state = self.previous_state
            self.previous_state = temp
            return True
        return False

    def get_state_name(self):
        return self.current_state.value

    def reset(self):
        self.previous_state = self.current_state
        self.current_state = GameState.MENU
