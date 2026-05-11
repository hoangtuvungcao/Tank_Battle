"""
Game — Vòng lặp game chính của Tank Battle.

Module này đóng vai trò là "bộ não" điều phối toàn bộ hoạt động của game.
Nó quản lý việc chuyển đổi giữa các màn hình (Menu, Chơi game, Pause), 
tải bản đồ, xử lý va chạm và điều khiển camera.
"""

import pygame # Thư viện game chính
import sys    # Thư viện hệ thống để thoát chương trình
from src.core.settings import * # Nhập tất cả các hằng số cài đặt
from src.core.state_manager import StateManager, GameState # Quản lý trạng thái game
from src.core.event_handler import EventHandler # Xử lý phím và chuột
from src.core.sound_manager import SoundManager # Quản lý âm thanh
from src.world.map import GameMap               # Lớp bản đồ
from src.world.camera import Camera             # Lớp camera theo dõi
from src.entities.player import Player           # Lớp người chơi
from src.entities.bullet_manager import BulletManager # Quản lý đạn
from src.ai.enemy import Enemy                   # Lớp kẻ địch
from src.ui.menu import MainMenu                 # Menu chính
from src.ui.settings_menu import SettingsMenu     # Menu cài đặt
from src.ui.tank_select_menu import TankSelectMenu # Menu chọn xe tăng
from src.ui.hud import HUD, LevelTransition      # Giao diện người dùng
from src.ui.particle import ParticleSystem       # Hệ thống hiệu ứng hạt (nổ, khói)


class Game:
    """
    Lớp điều khiển chính của toàn bộ trò chơi.
    """

    def __init__(self):
        """Khởi tạo các thành phần cơ bản của game."""
        pygame.init() # Khởi tạo thư viện Pygame
        # Tạo cửa sổ game với kích thước định sẵn
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # Đặt tiêu đề cho cửa sổ game
        pygame.display.set_caption(f"{GAME_TITLE} v{GAME_VERSION}")
        # Đối tượng quản lý thời gian và FPS
        self.clock = pygame.time.Clock()
        # Biến điều khiển vòng lặp chính
        self.running = True
        
        # --- Khởi tạo các module quản lý ---
        self.state_manager = StateManager() # Quản lý trạng thái (Menu/Play/...)
        self.event_handler = EventHandler() # Lắng nghe sự kiện bàn phím/chuột
        self.sound_manager = SoundManager() # Điều khiển nhạc và hiệu ứng âm thanh
        
        # --- Khởi tạo các thành phần giao diện ---
        self.menu = MainMenu()
        self.settings_menu = SettingsMenu()
        self.tank_select = TankSelectMenu()
        self.hud = HUD()
        self.level_transition = LevelTransition()
        self.particles = ParticleSystem()
        
        # --- Khởi tạo các thành phần logic game ---
        self.bullet_manager = BulletManager()
        self.game_map = GameMap()
        self.player = None     # Sẽ được khởi tạo khi vào màn
        self.enemies = []      # Danh sách chứa các xe tăng địch
        self.camera = None     # Sẽ được khởi tạo sau khi load map
        
        # --- Các thông số trạng thái game ---
        self.score = 0         # Điểm số
        self.level = 1         # Màn chơi hiện tại
        self.lives = PLAYER_LIVES # Số mạng còn lại
        self.invincible_timer = 0.0 # Thời gian bất tử khi vừa hồi sinh
        self.respawn_timer = 0.0    # Thời gian chờ để hồi sinh
        self.player_color = "green" # Màu xe tăng người chơi chọn
        self.damage_flash = 0.0     # Hiệu ứng nháy đỏ khi trúng đạn
        self.camera_shake = 0.0     # Hiệu ứng rung màn hình

    def run(self):
        """Vòng lặp game chính chạy liên tục cho đến khi thoát."""
        self.sound_manager.play_music("menu") # Phát nhạc menu lúc bắt đầu
        while self.running:
            # Giới hạn FPS và tính thời gian giữa 2 khung hình (dt - delta time)
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05) # Ngăn chặn hiện tượng giật lag quá mạnh
            
            # Cập nhật các sự kiện đầu vào
            self.event_handler.update()
            # Nếu người chơi bấm nút thoát cửa sổ
            if self.event_handler.is_quit_requested():
                self.running = False
                break
            
            # 1. Cập nhật logic (Tính toán tọa độ, va chạm, AI...)
            self._update(dt)
            # 2. Vẽ tất cả lên màn hình
            self._draw()
            # 3. Cập nhật hiển thị thực tế lên màn hình máy tính
            pygame.display.flip()
            
        pygame.quit() # Giải phóng bộ nhớ Pygame
        sys.exit()    # Thoát hệ thống

    def _update(self, dt):
        """Phân phối việc cập nhật tùy theo trạng thái game hiện tại."""
        state = self.state_manager.current_state
        
        if state == GameState.MENU:
            self.menu.update(dt)
            self._update_menu()
        elif state == GameState.SETTINGS:
            self.settings_menu.update(self.event_handler.get_mouse_pos())
            self._update_settings()
        elif state == GameState.TANK_SELECT:
            self.tank_select.update(self.event_handler.get_mouse_pos())
            self._update_tank_select()
        elif state == GameState.PLAYING:
            self._update_playing(dt)
        elif state == GameState.PAUSED:
            self._update_paused()
        elif state == GameState.GAME_OVER:
            self._update_game_over()
        elif state == GameState.LEVEL_TRANSITION:
            # Xử lý hiệu ứng chuyển màn, khi kết thúc sẽ load màn tiếp theo
            if self.level_transition.update(dt):
                self._load_level(self.level)
                self.state_manager.change_state(GameState.PLAYING)

    def _draw(self):
        """Phân phối việc vẽ tùy theo trạng thái game hiện tại."""
        state = self.state_manager.current_state
        
        if state == GameState.MENU:
            self.menu.draw(self.screen)
        elif state == GameState.SETTINGS:
            self.settings_menu.draw(self.screen)
        elif state == GameState.TANK_SELECT:
            self.tank_select.draw(self.screen)
        elif state == GameState.PLAYING:
            self._draw_playing()
        elif state == GameState.PAUSED:
            self._draw_playing() # Vẽ game đang chơi mờ ở dưới
            self._draw_pause_overlay() # Vẽ lớp phủ Tạm dừng
        elif state == GameState.GAME_OVER:
            self._draw_game_over()
        elif state == GameState.LEVEL_TRANSITION:
            self._draw_playing() # Vẽ game ở dưới
            self.level_transition.draw(self.screen) # Vẽ hiệu ứng chuyển màn

    def _update_menu(self):
        """Xử lý các sự kiện tại màn hình Menu chính."""
        for event in self.event_handler.get_events():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                result = self.menu.handle_click(event.pos)
                if result:
                    self.sound_manager.play_sfx("button") # Tiếng click nút
                if result == "start":
                    self.state_manager.change_state(GameState.TANK_SELECT)
                elif result == "settings":
                    self.state_manager.change_state(GameState.SETTINGS)
                elif result == "quit":
                    self.running = False

    def _update_settings(self):
        """Xử lý cài đặt âm lượng và hiển thị."""
        for event in self.event_handler.get_events():
            result = self.settings_menu.handle_event(event)
            if result:
                self.sound_manager.play_sfx("button")
                
            # Cập nhật âm lượng ngay lập tức để người dùng nghe thử
            self.sound_manager.set_music_volume(self.settings_menu.music_volume)
            self.sound_manager.set_sfx_volume(self.settings_menu.sfx_volume)
                
            if result == "back":
                # Áp dụng chế độ Toàn màn hình nếu được chọn
                current_fs = (self.screen.get_flags() & pygame.FULLSCREEN) != 0
                if self.settings_menu.fullscreen and not current_fs:
                    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
                elif not self.settings_menu.fullscreen and current_fs:
                    self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    
                self.state_manager.change_state(GameState.MENU)

    def _update_tank_select(self):
        """Xử lý chọn màu xe tăng và bắt đầu game."""
        for event in self.event_handler.get_events():
            result = self.tank_select.handle_event(event)
            if result:
                self.sound_manager.play_sfx("button")
            if result == "start":
                self.player_color = self.tank_select.selected_color
                # Reset các thông số khi bắt đầu game mới
                self.score = 0
                self.level = 1
                self.lives = PLAYER_LIVES
                self._load_level(self.level)
                self.sound_manager.play_music("game") # Đổi nhạc sang nhạc chiến đấu
                self.state_manager.change_state(GameState.PLAYING)
            elif result == "back":
                self.state_manager.change_state(GameState.MENU)

    def _load_level(self, level):
        """Tải bản đồ, tạo nhân vật và reset trạng thái cho một màn chơi mới."""
        self.game_map = GameMap()
        self.game_map.load_from_file(f"{MAPS_DIR}/level{level}.txt")
        px, py = self.game_map.get_player_spawn()
        
        # Khởi tạo hoặc reset Player
        if self.player is None:
            self.player = Player(px, py, self.player_color)
        else:
            self.player.reset(px, py)
            
        # Tạo danh sách kẻ địch dựa trên các điểm spawn trong file map
        self.enemies = []
        diff = self.settings_menu.difficulty # Lấy độ khó từ settings
        for ex, ey in self.game_map.get_enemy_spawns():
            self.enemies.append(Enemy(ex, ey, diff))
            
        # Khởi tạo hệ thống AI điều khiển bầy đàn
        from src.ai.ai_controller import AIController
        self.ai_controller = AIController(self.game_map)
        
        # Khởi tạo camera bao phủ toàn bộ map
        self.camera = Camera(self.game_map.get_pixel_width(), self.game_map.get_pixel_height())
        # Xóa sạch đạn và hiệu ứng cũ
        self.bullet_manager.clear()
        self.particles.clear_all()
        # Đặt thời gian bất tử khi vừa bắt đầu màn
        self.invincible_timer = RESPAWN_INVINCIBLE

    def _update_playing(self, dt):
        """Logic chính khi đang trong trận đấu."""
        # Kiểm tra nút tạm dừng (ESC)
        if self.event_handler.is_pause_pressed():
            self.state_manager.change_state(GameState.PAUSED)
            return
            
        # Giảm thời gian bất tử
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            
        # Xử lý khi player đang chờ hồi sinh
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                px, py = self.game_map.get_player_spawn()
                self.player.reset(px, py)
                self.invincible_timer = RESPAWN_INVINCIBLE
                self.sound_manager.play_sfx("respawn")
            return
            
        # Cập nhật logic Người chơi (Di chuyển, quay nòng)
        if self.player.is_alive():
            self.player.handle_input(self.event_handler.get_keys(),
                                     self.event_handler.get_mouse_pos(), dt,
                                     self.game_map, self.camera.offset_x, self.camera.offset_y)
            # Xử lý bắn đạn bằng phím SPACE
            for event in self.event_handler.get_events():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bd = self.player.handle_shoot()
                    if bd:
                        self.bullet_manager.add_bullet(bd) # Thêm đạn vào quản lý
                        self.sound_manager.play_sfx("shoot") # Tiếng bắn
                        self.particles.add_muzzle_flash(bd["x"], bd["y"], bd["angle"]) # Hiệu ứng lửa đầu nòng
                        
        # Cập nhật trí tuệ nhân tạo (AI) cho toàn bộ bầy đàn địch
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if hasattr(self, 'ai_controller'):
            self.ai_controller.update_swarm(alive_enemies, self.player, dt)
            
        # Cập nhật logic từng con địch riêng lẻ
        for enemy in self.enemies:
            if enemy.is_alive():
                bd = enemy.update_ai(dt, (self.player.x, self.player.y),
                                     self.game_map, self.player.in_stealth)
                if bd: # Nếu địch bắn
                    self.bullet_manager.add_bullet(bd)
                    self.sound_manager.play_sfx("shoot")
                    self.particles.add_muzzle_flash(bd["x"], bd["y"], bd["angle"])
                    
        # --- Cập nhật và kiểm tra va chạm của ĐẠN ---
        old_player_hp = self.player.health
        old_enemy_hp = {id(e): e.health for e in self.enemies if e.is_alive()}
        
        # Nếu đang bất tử, đạn không gây sát thương cho người chơi
        if self.invincible_timer > 0:
            all_tanks = [t for t in self.enemies if t.is_alive()]
        else:
            all_tanks = [self.player] + self.enemies
            
        self.bullet_manager.update_all(dt, all_tanks, self.game_map)
        
        # --- Xử lý phá hủy Thùng Phuy (Barrel) và Sát Thương Nổ Lan ---
        for bullet in self.bullet_manager.bullets:
            if bullet.active:
                tile = self.game_map.get_tile_at(bullet.x, bullet.y)
                if tile and tile.is_barrel():
                    row = int(bullet.y // TILE_SIZE)
                    col = int(bullet.x // TILE_SIZE)
                    neighbors = self.game_map._get_neighbors(row, col)
                    # Tạo vụ nổ tại thùng phuy
                    self.particles.add_explosion(bullet.x, bullet.y, color="orange", small=True)
                    self.sound_manager.play_sfx("explosion")
                    bullet.active = False # Xóa viên đạn
                    tile.destroy(neighbors) # Phá hủy tile thùng phuy
                    
                    # Tính toán sát thương nổ lan cho các xe tăng xung quanh
                    barrel_x = col * TILE_SIZE + TILE_SIZE / 2
                    barrel_y = row * TILE_SIZE + TILE_SIZE / 2
                    splash_radius = TILE_SIZE * 1.5
                    
                    for tank in all_tanks:
                        dist = ((tank.x - barrel_x)**2 + (tank.y - barrel_y)**2)**0.5
                        if dist <= splash_radius:
                            tank.take_damage(50) # Thùng nổ gây 50 sát thương
                            self.particles.add_explosion(tank.x, tank.y, color="red", small=True)
                            
        # --- Kiểm tra hiệu ứng trúng đạn ---
        if self.player.health < old_player_hp: # Người chơi bị trúng đạn
            self.sound_manager.play_sfx("player_hit")
            self.damage_flash = 0.3  # Màn hình nháy đỏ trong 0.3s
            self.camera_shake = 0.2  # Rung màn hình 0.2s
            self.particles.add_explosion(self.player.x, self.player.y, small=True)
            
        for enemy in self.enemies: # Địch bị trúng đạn
            if enemy.is_alive():
                old = old_enemy_hp.get(id(enemy), enemy.health)
                if enemy.health < old:
                    self.sound_manager.play_sfx("enemy_hit")
                    self.player.add_hit() # Tăng độ chính xác cho player
                    self.particles.add_explosion(enemy.x, enemy.y, small=True)
                    
        # --- Kiểm tra cái chết của kẻ địch ---
        for enemy in self.enemies:
            if not enemy.is_alive() and id(enemy) in old_enemy_hp:
                self.particles.add_explosion(enemy.x, enemy.y)
                self.sound_manager.play_sfx("explosion")
                self.player.add_kill() # Tăng số mạng tiêu diệt
                self.score += 100       # Cộng điểm
                self.hud.add_kill_message(getattr(enemy, 'name', 'Enemy')) # Hiển thị lên Kill Feed
                
        # --- Kiểm tra cái chết của người chơi ---
        if not self.player.is_alive():
            self.particles.add_explosion(self.player.x, self.player.y)
            self.sound_manager.play_sfx("player_die")
            self.lives -= 1 # Trừ mạng
            if self.lives <= 0:
                self.state_manager.change_state(GameState.GAME_OVER)
                return
            self.respawn_timer = RESPAWN_DELAY # Bắt đầu đếm ngược hồi sinh
            
        # --- Kiểm tra hoàn thành màn chơi ---
        if len([e for e in self.enemies if e.is_alive()]) == 0:
            if self.level < MAX_LEVEL:
                self.level += 1
                self.sound_manager.play_sfx("level_up")
                self.level_transition.start(self.level)
                self.state_manager.change_state(GameState.LEVEL_TRANSITION)
            else:
                self.sound_manager.play_sfx("victory") # Thắng toàn bộ game
                self.state_manager.change_state(GameState.GAME_OVER)
                
        # Cập nhật camera theo tọa độ player
        self.camera.update(self.player.x, self.player.y)
        # Xử lý hiệu ứng rung camera
        if self.camera_shake > 0:
            self.camera_shake -= dt
            import random
            self.camera.offset_x += random.randint(-3, 3)
            self.camera.offset_y += random.randint(-3, 3)
            
        # Giảm thời gian nháy đỏ màn hình
        if self.damage_flash > 0:
            self.damage_flash -= dt
            
        # Cập nhật các hệ thống khác
        self.particles.update_all(dt)
        self.player.update(dt)
        self.hud.update(dt)

    def _draw_playing(self):
        """Vẽ toàn bộ khung cảnh trận đấu."""
        self.screen.fill(COLOR_BLACK) # Xóa màn hình bằng màu đen
        
        # Lấy độ dời của camera
        cx, cy = self.camera.offset_x, self.camera.offset_y
        
        # Vẽ bản đồ
        self.game_map.draw(self.screen, int(cx), int(cy))
        
        # Vẽ các xe tăng địch
        for e in self.enemies:
            if e.is_alive():
                e.draw(self.screen, cx, cy)
                
        # Vẽ Người chơi (có hiệu ứng nháy khi đang bất tử)
        if self.player.is_alive():
            if self.invincible_timer > 0:
                if int(self.invincible_timer * 8) % 2 == 0:
                    self.player.draw(self.screen, cx, cy)
            else:
                self.player.draw(self.screen, cx, cy)
                
        # Vẽ đạn
        self.bullet_manager.draw_all(self.screen, cx, cy)
        # Vẽ các hiệu ứng cháy nổ
        self.particles.draw_all(self.screen, cx, cy)
        # Vẽ HUD (Thanh máu, điểm, minimap)
        alive_count = sum(1 for e in self.enemies if e.is_alive())
        self.hud.draw(self.screen, self.player, self.score, alive_count, self.level,
                      self.game_map, self.enemies, self.lives)
                      
        # Vẽ lớp phủ màu đỏ khi bị trúng đạn
        if self.damage_flash > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(100 * (self.damage_flash / 0.3))
            flash.fill((255, 0, 0, min(alpha, 100)))
            self.screen.blit(flash, (0, 0))

    def _update_paused(self):
        """Xử lý khi game đang tạm dừng."""
        if self.event_handler.is_pause_pressed():
            self.state_manager.change_state(GameState.PLAYING)
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.state_manager.change_state(GameState.MENU)
                self.sound_manager.play_music("menu")

    def _draw_pause_overlay(self):
        """Vẽ bảng thông báo tạm dừng."""
        o = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        o.fill((0,0,0,150)) # Làm tối màn hình game
        self.screen.blit(o, (0,0))
        from src.core.font import get_font
        f = get_font(56, bold=True)
        t = f.render("TẠM DỪNG", True, COLOR_WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-30)))
        sf = get_font(24)
        s = sf.render("ESC để tiếp tục • Q để về menu", True, COLOR_GRAY)
        self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2+30)))

    def _update_game_over(self):
        """Xử lý khi kết thúc game (Thắng hoặc Thua)."""
        for event in self.event_handler.get_events():
            if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.state_manager.change_state(GameState.MENU)
                self.sound_manager.play_music("menu")

    def _draw_game_over(self):
        """Vẽ màn hình kết quả cuối cùng."""
        self.screen.fill((20,10,10))
        from src.core.font import get_font
        f = get_font(56, bold=True)
        # Kiểm tra điều kiện thắng: vượt qua MAX_LEVEL hoặc giết sạch địch mà còn sống
        won = self.level > MAX_LEVEL or (self.lives > 0 and all(not e.is_alive() for e in self.enemies))
        
        if won:
            t = f.render("CHIẾN THẮNG!", True, COLOR_YELLOW)
        else:
            t = f.render("THẤT BẠI", True, COLOR_RED)
            
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-60)))
        
        sf = get_font(28)
        # Hiển thị điểm số và màn chơi đạt được
        self.screen.blit(sf.render(f"Điểm: {self.score}", True, COLOR_WHITE),
                         sf.render(f"Điểm: {self.score}",True,COLOR_WHITE).get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
        self.screen.blit(sf.render(f"Màn: {self.level}", True, COLOR_WHITE),
                         sf.render(f"Màn: {self.level}",True,COLOR_WHITE).get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2+35)))
        
        sf2 = get_font(20)
        self.screen.blit(sf2.render("Nhấn phím bất kỳ để về menu", True, COLOR_GRAY),
                         sf2.render("Nhấn phím bất kỳ để về menu",True,COLOR_GRAY).get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100)))
