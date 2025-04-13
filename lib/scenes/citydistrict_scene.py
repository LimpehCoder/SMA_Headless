from base_scene import BaseScene
import pygame
from objects.house import House  # Importing House class for house objects
from simctrl.simctrl import HouseController  # Importing HouseController for managing houses

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
class CityDistrictScene(BaseScene):  # Inherits from BaseScene
    def __init__(self, district_id):  # Accepts unique district identifier (e.g. 1, 2, 3)
        self.bg_color = (80, 60, 60)  # Background color (dark reddish-brown)
        self.name = f"City_District{district_id}"  # Generate name like "City_District1"
        self.district_id = district_id  # Store the district ID for potential logic use
        self.houses = [] 
        self.house_controller = HouseController(self)

    def update(self, dt, clock):
        self.house_controller.update(dt, clock)

    def render(self, screen):  # Draw the scene visuals
        screen.fill(self.bg_color)  # Fill with the district's color
        for house in self.houses:
            house.render(screen)
