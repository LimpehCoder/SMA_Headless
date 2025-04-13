from base_scene import BaseScene
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class StatisticsScene(BaseScene):  # Inherits from BaseScene to follow the same scene interface
    def __init__(self):
        self.bg_color = (20, 20, 20)  # Very dark background (almost black) for contrast
        self.name = "Statistics"  # Scene name used for rendering and identification

    def render(self, screen):  # Draw method for this scene
        screen.fill(self.bg_color)  # Fill the entire screen with the background color
        font = pygame.font.SysFont("Arial", 48)  # Create a font object for drawing text
        label = font.render(self.name, True, (255, 255, 255))  # Render the scene name in white
        screen.blit(label, (50, 50))  # Draw the label at position (50, 50) on screen