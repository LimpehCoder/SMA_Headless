import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_scene import BaseScene
import pygame
from pygame.math import Vector2

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class SortingAreaScene(BaseScene):
    def __init__(self, carpark_ref):
        self.carpark = carpark_ref  # Reference to the carpark scene (used to access vans/cars)
        self.bg_color = (60, 70, 90)  # Background color for the canvas
        self.name = "SortingArea"  # Scene identifier
        self.couriers = []  # List of couriers in this scene
        self.boxes = []  # List of boxes currently in the sorting area
        self.truck = None
        self.box_pile = None
        self.spawned_today = False  # Tracks whether couriers have been spawned today
        self.spawned_cycles = set()  # Tracks which box spawn cycles have run
        self.pending_couriers = []  # Queue of couriers waiting to enter the canvas
        self.courier_spawn_timer = 0  # Timer used to space out entry of couriers
        self.courier_spawn_interval = 300  # Delay between courier entries (ms)
        self.door_to_carpark_rect = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2 - 32, 32, 32)

    def assign_idle_positions(self):
        top_start_x = SCREEN_WIDTH - 50  # Starting X position for staff couriers (top right of screen)
        top_start_y = 80  # Starting Y position for staff couriers (near top of screen)
        bottom_start_x = SCREEN_WIDTH - 50  # Starting X for subcontractors (bottom right of screen)
        bottom_start_y = SCREEN_HEIGHT - 160  # Y offset for subcontractors (near bottom of screen, adjust as needed)
        spacing = 35  # Horizontal and vertical spacing between couriers
        cols = 15  # Number of columns in the formation grid

        for index, courier in enumerate(self.couriers):  # Iterate over all couriers
            if courier.status not in ["Idle", "Ready"] or courier.queue_index is not None or courier.status in ["Move_to_Queue", "Queuing"]:  # Only assign idle and unassigned couriers

                if courier.type == "Courier_Staff":  # For staff couriers (entering from top)
                    col = index % cols  # Column index based on order
                    row = index // cols  # Row index based on order
                    target_x = top_start_x - (col * spacing)  # Calculate X position in grid
                    target_y = top_start_y + (row * spacing)  # Calculate Y position in grid

                elif courier.type == "Courier_Subcon":  # For subcontractor couriers (entering from bottom)
                    col = index % cols
                    row = index // cols
                    target_x = bottom_start_x - (col * spacing)  # Same as above, just with different origin
                    target_y = bottom_start_y + (row * spacing)

                courier.target_position = Vector2(target_x, target_y)  # Set movement target
                courier.status = "Forming"  # Begin animation to form-up point
                courier.grid_assigned = True  # Mark as assigned to prevent reassignment



    def receive_courier(self, courier):
        courier.status = "Entering"
        courier.position = pygame.Vector2(SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2)  # Spawn from right edge
        courier.target_position = pygame.Vector2(SCREEN_WIDTH - 200, SCREEN_HEIGHT // 2)  # Walk left into view
        courier.grid_assigned = False
        self.couriers.append(courier)

    def render(self, screen):
        screen.fill(self.bg_color)  # Fill background
        # Draw door rectangle
        pygame.draw.rect(screen, (0, 0, 0), self.door_to_carpark_rect)  # Black portal

        # Label for the door
        door_font = pygame.font.SysFont("Arial", 20)
        door_label = door_font.render("TO CARPARK", True, (0, 0, 0))
        screen.blit(door_label, (self.door_to_carpark_rect.x - 20, self.door_to_carpark_rect.y - 24))

        for c in self.couriers:
            c.render(screen)  # Draw each courier
        if self.truck:
            self.truck.render(screen)
        if self.box_pile:
            self.box_pile.render(screen)
        