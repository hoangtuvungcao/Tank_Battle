import pygame
from src.core.settings import (
    MUSIC_VOLUME, SFX_VOLUME, SOUNDS_DIR,
    MUSIC_MENU, MUSIC_GAME, SFX_SHOOT, SFX_EXPLOSION,
    SFX_HIT, SFX_BUTTON, SFX_LEVEL_UP,
    SFX_PLAYER_DIE, SFX_RESPAWN, SFX_ENEMY_HIT,
    SFX_PLAYER_HIT, SFX_VICTORY
)


class SoundManager:
    """Quản lý nhạc nền và hiệu ứng âm thanh. Không crash nếu thiếu file."""

    def __init__(self):
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.enabled = True
        self._sfx_cache = {}
        self._current_music = None
        
        # BẢNG ĐIỀU CHỈNH TAY ÂM LƯỢNG TỪNG LOẠI ÂM THANH (1.0 = 100%, 0.5 = 50%)
        # Bạn có thể thay đổi các con số ở đây để chỉnh to/nhỏ cho từng file âm thanh
        self.individual_volumes = {
            "menu_music": 1.0,   # Nhạc nền ngoài menu
            "game_music": 0.7,   # Nhạc nền trong lúc chơi game
            "shoot": 0.8,
            "explosion": 1.0,
            "hit": 0.8,
            "button": 0.2,       # Giảm tiếng click xuống 20% để không bị chói tai
            "level_up": 1.0,
            "player_die": 1.0,
            "respawn": 0.8,
            "enemy_hit": 0.7,
            "player_hit": 1.0,
            "victory": 1.0,
        }
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error:
            self.enabled = False

    def play_music(self, music_type):
        if not self.enabled:
            return
        duong_dan = MUSIC_MENU if music_type == "menu" else MUSIC_GAME
        if duong_dan == self._current_music:
            return
        try:
            pygame.mixer.music.load(duong_dan)
            multiplier = self.individual_volumes.get(f"{music_type}_music", 1.0)
            pygame.mixer.music.set_volume(self.music_volume * multiplier)
            pygame.mixer.music.play(loops=-1)
            self._current_music = duong_dan
        except (pygame.error, FileNotFoundError):
            pass

    def stop_music(self):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
            self._current_music = None
        except pygame.error:
            pass

    def play_sfx(self, sfx_name):
        if not self.enabled:
            return
        sfx_map = {
            "shoot": SFX_SHOOT, "explosion": SFX_EXPLOSION, "hit": SFX_HIT,
            "button": SFX_BUTTON, "level_up": SFX_LEVEL_UP, "player_die": SFX_PLAYER_DIE,
            "respawn": SFX_RESPAWN, "enemy_hit": SFX_ENEMY_HIT,
            "player_hit": SFX_PLAYER_HIT, "victory": SFX_VICTORY,
        }
        duong_dan = sfx_map.get(sfx_name)
        if duong_dan is None:
            return
        if sfx_name not in self._sfx_cache:
            try:
                sound = pygame.mixer.Sound(duong_dan)
                self._sfx_cache[sfx_name] = sound
            except (pygame.error, FileNotFoundError):
                return
        try:
            sound = self._sfx_cache[sfx_name]
            # Nhân âm lượng tổng (trong menu Cài đặt) với âm lượng riêng của từng file
            multiplier = self.individual_volumes.get(sfx_name, 1.0)
            final_volume = self.sfx_volume * multiplier
            sound.set_volume(final_volume)
            sound.play()
        except pygame.error:
            pass

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            multiplier = 1.0
            if self._current_music == MUSIC_MENU:
                multiplier = self.individual_volumes.get("menu_music", 1.0)
            elif self._current_music == MUSIC_GAME:
                multiplier = self.individual_volumes.get("game_music", 1.0)
            pygame.mixer.music.set_volume(self.music_volume * multiplier)
        except pygame.error:
            pass

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop_music()

    def fade_out_music(self, duration_ms=1000):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.fadeout(duration_ms)
            self._current_music = None
        except pygame.error:
            pass
