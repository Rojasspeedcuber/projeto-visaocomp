import pygame
from player import Player
from obstacles import ObstacleManager

class Game:
    """Controla a lógica principal do jogo"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Estados do jogo
        self.state = 'calibrating'  # 'calibrating', 'playing', 'game_over'

        # Objetos do jogo
        self.player = Player(screen_width, screen_height)
        self.obstacle_manager = ObstacleManager(screen_width, screen_height)

        # Pontuação
        self.score = 0
        self.frame_count = 0

        # Debug
        self.debug_mode = False

        # Fontes
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

    def update(self, pose_state):
        """Atualiza estado do jogo"""

        # Estado: Calibrando
        if self.state == 'calibrating':
            if pose_state['is_calibrated']:
                self.state = 'playing'
            return

        # Estado: Jogando
        if self.state == 'playing':
            # Atualiza jogador
            self.player.update(pose_state)

            # Atualiza obstáculos
            self.obstacle_manager.update(self.score)

            # Verifica colisão
            if self.obstacle_manager.check_collision(self.player.get_rect()):
                self.state = 'game_over'
                return

            # Atualiza pontuação (1 ponto a cada segundo)
            self.frame_count += 1
            if self.frame_count >= 60:
                self.frame_count = 0
                self.score += 1

    def draw(self, screen, camera_frame, pose_state):
        """Desenha todos os elementos do jogo"""
        # Fundo
        screen.fill((20, 20, 40))

        # Mostra câmera de fundo (opcional)
        if camera_frame is not None:
            # Redimensiona para caber
            cam_surface = pygame.surfarray.make_surface(camera_frame.swapaxes(0, 1))
            cam_surface = pygame.transform.scale(cam_surface, (self.screen_width, self.screen_height))
            cam_surface.set_alpha(30)  # Transparência
            screen.blit(cam_surface, (0, 0))

        # Desenha chão
        pygame.draw.rect(screen, (50, 50, 70),
                        (0, self.screen_height - 100, self.screen_width, 100))

        # Estado: Calibrando
        if self.state == 'calibrating':
            self.draw_calibration_screen(screen, pose_state)
            return

        # Estado: Jogando
        if self.state == 'playing':
            self.obstacle_manager.draw(screen)
            self.player.draw(screen)
            self.draw_hud(screen, pose_state)

        # Estado: Game Over
        elif self.state == 'game_over':
            self.obstacle_manager.draw(screen)
            self.player.draw(screen)
            self.draw_game_over(screen)

        # Modo Debug
        if self.debug_mode:
            self.draw_debug_info(screen, pose_state)

    def draw_calibration_screen(self, screen, pose_state):
        """Tela de calibração"""
        # Título
        title = self.font_large.render("CALIBRANDO...", True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))

        # Instruções
        instructions = [
            "Posicione-se em frente à câmera",
            "Mantenha-se na posição neutra",
            "Aguarde a calibração..."
        ]

        y = 250
        for text in instructions:
            rendered = self.font_small.render(text, True, (200, 200, 200))
            screen.blit(rendered, (self.screen_width // 2 - rendered.get_width() // 2, y))
            y += 50

        # Barra de progresso
        progress = pose_state.get('calibration_progress', 0)
        bar_width = 400
        bar_height = 30
        bar_x = self.screen_width // 2 - bar_width // 2
        bar_y = 450

        # Fundo da barra
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Progresso
        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, (0, 255, 100), (bar_x, bar_y, fill_width, bar_height))

        # Borda
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Percentual
        percent_text = self.font_small.render(f"{int(progress * 100)}%", True, (255, 255, 255))
        screen.blit(percent_text, (self.screen_width // 2 - percent_text.get_width() // 2, bar_y + 40))

    def draw_hud(self, screen, pose_state):
        """Desenha HUD (pontuação e info)"""
        # Pontuação
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))

        # Velocidade atual
        speed_text = self.font_small.render(
            f"Speed: {self.obstacle_manager.current_speed:.1f}",
            True, (200, 200, 200)
        )
        screen.blit(speed_text, (20, 70))

        # Indicadores de estado
        y = self.screen_height - 60
        if pose_state['is_jumping']:
            jump_text = self.font_small.render("^ PULANDO", True, (255, 255, 0))
            screen.blit(jump_text, (20, y))

        if pose_state['is_crouching']:
            crouch_text = self.font_small.render("v AGACHADO", True, (255, 200, 0))
            screen.blit(crouch_text, (20, y - 35))

    def draw_game_over(self, screen):
        """Tela de Game Over"""
        # Overlay escuro
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Texto Game Over
        game_over_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
        screen.blit(game_over_text,
                   (self.screen_width // 2 - game_over_text.get_width() // 2, 200))

        # Pontuação final
        score_text = self.font_medium.render(f"Pontuação: {self.score}", True, (255, 255, 255))
        screen.blit(score_text,
                   (self.screen_width // 2 - score_text.get_width() // 2, 300))

        # Instruções
        restart_text = self.font_small.render("Pressione R para reiniciar", True, (200, 200, 200))
        screen.blit(restart_text,
                   (self.screen_width // 2 - restart_text.get_width() // 2, 400))

        quit_text = self.font_small.render("Pressione Q para sair", True, (200, 200, 200))
        screen.blit(quit_text,
                   (self.screen_width // 2 - quit_text.get_width() // 2, 450))

    def draw_debug_info(self, screen, pose_state):
        """Desenha informações de debug"""
        debug_y = self.screen_height - 150

        debug_info = [
            f"X Position: {pose_state['x_position']:.2f}",
            f"Jumping: {pose_state['is_jumping']}",
            f"Crouching: {pose_state['is_crouching']}",
            f"Obstacles: {len(self.obstacle_manager.obstacles)}",
            f"FPS: 60 (target)"
        ]

        # Fundo semi-transparente
        debug_bg = pygame.Surface((250, 130))
        debug_bg.set_alpha(150)
        debug_bg.fill((0, 0, 0))
        screen.blit(debug_bg, (self.screen_width - 270, debug_y - 10))

        for i, text in enumerate(debug_info):
            rendered = self.font_small.render(text, True, (0, 255, 0))
            screen.blit(rendered, (self.screen_width - 260, debug_y + i * 25))

    def restart(self):
        """Reinicia o jogo"""
        self.state = 'playing'
        self.score = 0
        self.frame_count = 0
        self.player = Player(self.screen_width, self.screen_height)
        self.obstacle_manager.reset()

    def toggle_debug(self):
        """Alterna modo debug"""
        self.debug_mode = not self.debug_mode
