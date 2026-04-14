import pygame

class Player:
    """Representa o jogador controlado por visão computacional"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Dimensões do jogador
        self.width = 40
        self.height = 60
        self.normal_height = 60
        self.crouch_height = 35

        # Posição inicial
        self.x = screen_width // 2
        self.y = screen_height - 150
        self.base_y = self.y

        # Física do pulo
        self.jump_velocity = 0
        self.is_jumping = False
        self.jump_speed = -15
        self.gravity = 0.8

        # Estados
        self.is_crouching = False

        # Cor
        self.color = (0, 200, 255)

    def update(self, pose_state):
        """Atualiza posição do jogador baseado no estado da pose"""
        if not pose_state['is_calibrated']:
            return

        # 1. Movimento horizontal (posição X normalizada 0-1)
        target_x = int(pose_state['x_position'] * self.screen_width)

        # Limita aos bounds da tela
        margin = self.width // 2
        target_x = max(margin, min(self.screen_width - margin, target_x))

        # Suaviza movimento
        self.x += (target_x - self.x) * 0.3

        # 2. Pulo
        if pose_state['is_jumping'] and not self.is_jumping and not self.is_crouching:
            self.is_jumping = True
            self.jump_velocity = self.jump_speed

        # Física do pulo
        if self.is_jumping:
            self.y += self.jump_velocity
            self.jump_velocity += self.gravity

            # Aterrissagem
            if self.y >= self.base_y:
                self.y = self.base_y
                self.is_jumping = False
                self.jump_velocity = 0

        # 3. Agachar
        self.is_crouching = pose_state['is_crouching'] and not self.is_jumping

        if self.is_crouching:
            self.height = self.crouch_height
            self.y = self.base_y + (self.normal_height - self.crouch_height)
        else:
            self.height = self.normal_height
            if not self.is_jumping:
                self.y = self.base_y

    def get_rect(self):
        """Retorna retângulo de colisão"""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y,
            self.width,
            self.height
        )

    def draw(self, screen):
        """Desenha o jogador"""
        rect = self.get_rect()

        # Corpo
        pygame.draw.rect(screen, self.color, rect, border_radius=5)

        # Olhos
        eye_y = rect.y + 15
        pygame.draw.circle(screen, (255, 255, 255), (rect.x + 12, eye_y), 4)
        pygame.draw.circle(screen, (255, 255, 255), (rect.x + 28, eye_y), 4)
        pygame.draw.circle(screen, (0, 0, 0), (rect.x + 12, eye_y), 2)
        pygame.draw.circle(screen, (0, 0, 0), (rect.x + 28, eye_y), 2)

        # Indicador de estado
        if self.is_jumping:
            # Desenha efeito de pulo
            pygame.draw.circle(screen, (255, 255, 0),
                             (int(self.x), rect.bottom + 5), 8, 2)

        if self.is_crouching:
            # Desenha efeito de agachar
            pygame.draw.rect(screen, (255, 200, 0),
                           (rect.x - 5, rect.bottom, rect.width + 10, 3))
