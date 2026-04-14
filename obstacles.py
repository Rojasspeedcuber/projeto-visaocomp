import pygame
import random

class Obstacle:
    """Representa um obstáculo individual"""

    def __init__(self, x, y, obstacle_type, speed):
        self.x = x
        self.y = y
        self.type = obstacle_type  # 'high', 'mid', 'low'
        self.speed = speed

        # Dimensões baseadas no tipo
        if obstacle_type == 'high':
            self.width = 40
            self.height = 80
            self.color = (255, 50, 50)
        elif obstacle_type == 'mid':
            self.width = 50
            self.height = 50
            self.color = (255, 150, 50)
        else:  # low
            self.width = 60
            self.height = 30
            self.color = (255, 200, 50)

    def update(self):
        """Move obstáculo para baixo"""
        self.y += self.speed

    def get_rect(self):
        """Retorna retângulo de colisão"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen):
        """Desenha o obstáculo"""
        rect = self.get_rect()
        pygame.draw.rect(screen, self.color, rect, border_radius=5)

        # Borda
        pygame.draw.rect(screen, (200, 0, 0), rect, 2, border_radius=5)

    def is_off_screen(self, screen_height):
        """Verifica se saiu da tela"""
        return self.y > screen_height


class ObstacleManager:
    """Gerencia geração e atualização de obstáculos"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.obstacles = []

        # Configurações de spawn
        self.spawn_timer = 0
        self.base_spawn_rate = 60  # frames entre spawns
        self.current_spawn_rate = self.base_spawn_rate
        self.base_speed = 4
        self.current_speed = self.base_speed

        # Dificuldade progressiva
        self.difficulty_timer = 0
        self.difficulty_increase_rate = 600  # frames (10 segundos a 60 FPS)

    def update(self, score):
        """Atualiza obstáculos e gera novos"""
        # Atualiza obstáculos existentes
        for obstacle in self.obstacles[:]:
            obstacle.update()

            # Remove se saiu da tela
            if obstacle.is_off_screen(self.screen_height):
                self.obstacles.remove(obstacle)

        # Aumenta dificuldade ao longo do tempo
        self.difficulty_timer += 1
        if self.difficulty_timer >= self.difficulty_increase_rate:
            self.difficulty_timer = 0
            self.current_speed = min(self.base_speed + score // 10, 12)
            self.current_spawn_rate = max(self.base_spawn_rate - score // 5, 30)

        # Gera novos obstáculos
        self.spawn_timer += 1
        if self.spawn_timer >= self.current_spawn_rate:
            self.spawn_timer = 0
            self.spawn_obstacle()

    def spawn_obstacle(self):
        """Gera um novo obstáculo aleatório"""
        # Tipo aleatório
        obstacle_type = random.choice(['high', 'mid', 'low'])

        # Posição X aleatória (evita bordas)
        margin = 60
        x = random.randint(margin, self.screen_width - margin - 60)

        # Cria obstáculo
        obstacle = Obstacle(x, -50, obstacle_type, self.current_speed)
        self.obstacles.append(obstacle)

    def draw(self, screen):
        """Desenha todos os obstáculos"""
        for obstacle in self.obstacles:
            obstacle.draw(screen)

    def check_collision(self, player_rect):
        """Verifica colisão com o jogador"""
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                return True
        return False

    def reset(self):
        """Reseta obstáculos"""
        self.obstacles = []
        self.spawn_timer = 0
        self.current_spawn_rate = self.base_spawn_rate
        self.current_speed = self.base_speed
        self.difficulty_timer = 0
