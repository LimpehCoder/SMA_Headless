from pygame.math import Vector2
from loadimage import load_image
import pygame  # Importing pygame for rendering and font handling
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720  # Dimensions used throughout the GUI

class Van:
    def __init__(self, position, scene_name="Carpark"):
        self.position = Vector2(SCREEN_WIDTH + 100, position.y)  # Off-screen right
        self.target_position = Vector2(position)  # The in-scene location the van should drive to
        self.scene = scene_name  # Track which scene the van belongs to (e.g., "Carpark")
        self.occupied = False  # Whether a courier has claimed this van
        self.driver = None  # Reference to the assigned courier
        self.speed = 120  # Movement speed in pixels per second
        self.image = load_image("van.png", (18, 12))  # Load and scale the van image
        self.box_load = 0  # Start with zero boxes loaded
        self.font = pygame.font.SysFont("Arial", 16)

    def update(self, dt):
        direction = self.target_position - self.position  # Get vector to target
        if direction.length() > 1:  # If far enough from destination, move
            direction.normalize_ip()  # Normalize to unit direction vector
            self.position += direction * self.speed * (dt / 1000.0)  # Move based on speed and time delta

    def loaded_box(self):
        self.box_load += 1

    def unload_box(self):
        self.box_load = max(0, self.box_load - 1)


    def render(self, screen):
        screen.blit(self.image, self.position)  # Draw van at its current position
        if self.box_load > 0:
            label = self.font.render(str(self.box_load), True, (255, 255, 255))
            screen.blit(label, (self.position.x + 10, self.position.y - 20))  # Position above the vehicle
