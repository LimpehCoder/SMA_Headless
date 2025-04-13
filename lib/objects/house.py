from pygame.math import Vector2
from loadimage import load_image
import pygame  # Importing pygame for rendering and font handling
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720  # Dimensions used throughout the GUI

class House:
    def __init__(self, scene_name="Neighborhood"):
        self.position = None  # Will be set later
        self.scene = scene_name
        self.image = load_image("house.png", (18, 18))
        self.font = pygame.font.SysFont("Arial", 16)
        self.occupied = False  # Renamed for clarity (optional)

    def render(self, screen):
        if self.position is not None:
            screen.blit(self.image, self.position)
            if self.occupied:
                label = self.font.render("Occupied", True, (255, 255, 255))
                screen.blit(label, (self.position.x + 5, self.position.y - 20))