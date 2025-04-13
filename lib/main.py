import pygame
import random
import math
import os
from collections import deque
from enum import Enum
import pygame_gui

# --- Import core components from simctrl.py ---
from simctrl.simctrl import SceneManager, SimulationClock, TruckController
from simctrl.van_ctrl import VanController
from simctrl.car_ctrl import CarController
from simctrl.courier_ctrl import CourierController, StaffController,SubconController
from scenes import sortingarea_scene, carpark_scene, citydistrict_scene, control_panel_stats

# Initialize scenes and controller
scene_manager = SceneManager()  # Create the global scene manager that handles switching and tracking active scenes
carpark = carpark_scene.CarparkScene()  # Instantiate the carpark scene
sorting_area_scene = sortingarea_scene.SortingAreaScene(carpark)  # Instantiate sorting area scene with reference to carpark
# Initialize controllers
truck_controller = TruckController(sorting_area_scene)
van_controller = VanController(carpark)
car_controller = CarController(carpark)
staff_controller = StaffController(sorting_area_scene, carpark, scene_manager)
subcon_controller = SubconController(sorting_area_scene, carpark, scene_manager)

# Initialize Pygame and simulation window
pygame.init()  # Initialize all imported Pygame modules
screen = pygame.display.set_mode((1280, 720))  # Create a window of size 1280x720
clock = pygame.time.Clock()  # Track time per frame for consistent simulation speed
sim_clock = SimulationClock()  # Custom clock to simulate in-game time progression
# Screen and simulation constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720  # Dimensions used throughout the GUI
FPS = 60  # Frame rate cap
VAN_CAPACITY = 50  # Not used here directly, probably for delivery logic
CAR_CAPACITY = 50  # Ditto
CYCLE_TIMES = {  # Box delivery cycle timing (hours)
    "ACycle": 8,
    "BCycle": 13,
    "NCycle": 18
}
WORKDAY_START = 6  # Start hour of simulation day
WORKDAY_END = 22  # End hour of simulation day
SPRITE_PATH = "assets/sprites/"  # Base path for sprite images
HOUSE_GRID = [(x, y) for x in range(0, 900, 30) for y in range(0, 900, 30)]  # Grid of delivery points for houses

# Register scenes
scene_manager.add_scene("Carpark", carpark)  # Add the carpark scene to the manager
scene_manager.add_scene("SortingArea", sorting_area_scene)  # Add sorting area scene
scene_manager.add_scene("City_District1", citydistrict_scene.CityDistrictScene(1))  # Add city district 1
scene_manager.add_scene("City_District2", citydistrict_scene.CityDistrictScene(2))  # Add city district 2
scene_manager.add_scene("City_District3", citydistrict_scene.CityDistrictScene(3))  # Add city district 3
scene_manager.add_scene("Statistics", control_panel_stats.StatisticsScene())  # Add statistics scene
scene_manager.switch_scene("SortingArea")  # Start on the Carpark scene
sorting_area_scene.door_to_carpark_target = carpark
carpark.door_to_sorting_target = sorting_area_scene

# UI Manager and scene buttons
ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))  # Setup GUI manager for handling buttons

# Create UI buttons to allow switching scenes with mouse clicks
button_sorting = pygame_gui.elements.UIButton(pygame.Rect((20, 640), (180, 40)), 'Sorting Area', ui_manager)
button_carpark = pygame_gui.elements.UIButton(pygame.Rect((220, 640), (180, 40)), 'Carpark', ui_manager)
button_city1 = pygame_gui.elements.UIButton(pygame.Rect((420, 640), (180, 40)), 'City District 1', ui_manager)
button_city2 = pygame_gui.elements.UIButton(pygame.Rect((620, 640), (180, 40)), 'City District 2', ui_manager)
button_city3 = pygame_gui.elements.UIButton(pygame.Rect((820, 640), (180, 40)), 'City District 3', ui_manager)
button_stats = pygame_gui.elements.UIButton(pygame.Rect((1020, 640), (180, 40)), 'Statistics', ui_manager)

# Simulation flags
isNPI = False  # Toggle for Non-Performance Indicator mode (could affect behavior)
isSurge = False  # Toggle for surge traffic or load conditions
current_canvas = "Carpark"  # Initial canvas set for reference

# Entity trackers
all_couriers = []  # Could be used for stats or persistence
all_vehicles = []  # Same
all_boxes = []  # Same
undelivered_boxes = deque()  # A FIFO queue of undelivered boxes (for routing)
stat_tracker = {}  # Dictionary to store simulation stats

CourierController.initialize_idle_grids()
# Main game loop
running = True  # Flag to keep the game loop alive
while running:
    dt = clock.tick(FPS)  # Cap FPS and retrieve time since last frame (in ms)
    for event in pygame.event.get():  # Get all queued events (keyboard, mouse, etc.)
        if event.type == pygame.QUIT:
            running = False  # Quit the loop if the window is closed

        if event.type == pygame.KEYDOWN:  # Keyboard-based scene switching
            if event.key == pygame.K_1:
                scene_manager.switch_scene("SortingArea")
            elif event.key == pygame.K_2:
                scene_manager.switch_scene("Carpark")
            elif event.key == pygame.K_3:
                scene_manager.switch_scene("City_District1")
            elif event.key == pygame.K_4:
                scene_manager.switch_scene("City_District2")
            elif event.key == pygame.K_5:
                scene_manager.switch_scene("City_District3")
            elif event.key == pygame.K_6:
                scene_manager.switch_scene("Statistics")

        ui_manager.process_events(event)  # Let GUI respond to this event

        if event.type == pygame_gui.UI_BUTTON_PRESSED:  # Scene switch buttons
            if event.ui_element == button_sorting:
                scene_manager.switch_scene("SortingArea")
            elif event.ui_element == button_carpark:
                scene_manager.switch_scene("Carpark")
            elif event.ui_element == button_city1:
                scene_manager.switch_scene("City_District1")
            elif event.ui_element == button_city2:
                scene_manager.switch_scene("City_District2")
            elif event.ui_element == button_city3:
                scene_manager.switch_scene("City_District3")
            elif event.ui_element == button_stats:
                scene_manager.switch_scene("Statistics")

        scene_manager.handle_event(event)  # Forward the event to the active scene

    # Run simulation
    sim_clock.update(dt)  # Advance in-game time
    # Modular simulation logic
    truck_controller.update(dt, sim_clock)
    van_controller.update(dt, sim_clock)
    car_controller.update(dt, sim_clock)
    staff_controller.report(dt, sim_clock)
    subcon_controller.report(dt, sim_clock)  # Update all subcon staff
    scene_manager.update_all(dt, sim_clock)  # Update all scenes
    ui_manager.update(dt / 1000.0)  # Update UI (needs seconds, not ms)

    # Draw scene
    scene_manager.render(screen)  # Draw active scene content

    # Display simulation time and current scene overlay
    font = pygame.font.SysFont("Arial", 24)
    time_text = font.render(sim_clock.get_time_str(), True, (255, 255, 255))  # Render current sim time
    scene_text = font.render(f"Scene: {scene_manager.current_scene}", True, (255, 255, 255))  # Active scene name
    screen.blit(time_text, (20, 20))  # Show time top-left
    screen.blit(scene_text, (20, 50))  # Show scene name below

    ui_manager.draw_ui(screen)  # Draw UI elements
    pygame.display.flip()  # Refresh the screen with all updates

pygame.quit()  # Shut down Pygame cleanly when the loop ends
