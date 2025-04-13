import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_scene import BaseScene
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class CarparkScene(BaseScene):  # Inherits from BaseScene
    def __init__(self):
        self.bg_color = (30, 80, 60)  # Set background color (dark greenish)
        self.name = "Carpark"  # Scene name for labeling
        self.door_to_sorting_rect = pygame.Rect(50, SCREEN_HEIGHT // 2 - 32, 32, 32)  # Left edge
        self.vans = []  # List to store van objects
        self.cars = []  # List to store car objects
        self.spawned_today = False  # Tracks if today's vehicles have been spawned

    def receive_courier(self, courier):
        courier.status = "Entering"
        courier.position = pygame.Vector2(100, SCREEN_HEIGHT // 2)  # Set spawn-in position
        courier.target_position = pygame.Vector2(200, SCREEN_HEIGHT // 2)  # Move right into formation
        courier.grid_assigned = False
        self.vans.append(courier)  # Or: self.couriers.append() if you track separately

    def update(self, dt, sim_clock):
        # Update vehicle positions and states
        for van in self.vans:
            van.update(dt)
        for car in self.cars:
            car.update(dt)

    def render(self, screen):  # Draws everything on this scene
        screen.fill(self.bg_color)  # Fill background with carpark color
        pygame.draw.rect(screen, (0, 0, 0), self.door_to_sorting_rect)  # Black portal to SortingArea
        door_font = pygame.font.SysFont("Arial", 20)
        door_label = door_font.render("TO SORTING", True, (255, 255, 255))
        screen.blit(door_label, (self.door_to_sorting_rect.x - 40, self.door_to_sorting_rect.y - 24))

        for van in self.vans:  # Draw each van
            van.render(screen)

        for car in self.cars:  # Draw each car
            car.render(screen)