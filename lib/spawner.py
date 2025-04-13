import pygame
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pygame.math import Vector2

from objects.courier import Courier, StaffCourier, SubconCourier  # Import Courier class from courier module
from objects.van import Van
from objects.car import Car  # Import vehicle classes from vehicles module
from objects.box import BoxPile  # Import Box class from box module
from objects.truck import Truck  # Import Truck class from truck module
from objects.house import House  # Import House class from house module

CYCLE_TIMES = {
    "ACycle": 8,
    "BCycle": 13,
    "NCycle": 18
}

COURIER_ENTRY_POINT = pygame.Vector2(-50, 300)  # Starting position (offscreen)
COURIER_ENTRY_TARGET = pygame.Vector2(150, 300)  # Entry target position on screen
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720  # Dimensions used throughout the GUI

# --- Spawner Functions ---

def spawn_vans(vans_list):
    vans_list.clear()
    spacing = 50
    right_x = SCREEN_WIDTH - 50
    top_y = 60

    van_cols = 8
    van_rows = 5
    van_start_x = right_x
    van_start_y = top_y

    for row in range(van_rows):
        for col in range(van_cols):
            x = van_start_x - col * spacing
            y = van_start_y + row * spacing
            vans_list.append(Van(position=Vector2(x, y)))

    print(f"Spawned {len(vans_list)} vans")

def spawn_cars(cars_list):
    cars_list.clear()

    spacing = 50
    grid_spacing = 10
    top_y = 60
    gap = 50

    full_cols = 8
    half_cols = 4
    car_rows = 5

    right_x = SCREEN_WIDTH - 50  # right edge of vans
    van_cols = 8
    van_width = van_cols * spacing
    van_left_edge = right_x - van_width

    # --- Top row: half grid + full grid next to vans with one uniform gap
    top_car_grids = [
        {'cols': half_cols},  # placed first (leftmost)
        {'cols': full_cols}   # placed second, flush with vans
    ]

    # Position full car grid's rightmost car to be just left of vans
    full_car_grid_right_edge = van_left_edge - grid_spacing

    # Compute the x of the rightmost car in the full car grid
    car_start_x = full_car_grid_right_edge

    for grid in reversed(top_car_grids):  # Place right-to-left
        cols = grid['cols']
        car_start_y = top_y

        for row in range(car_rows):
            for col in range(cols):
                x = car_start_x - col * spacing
                y = car_start_y + row * spacing
                cars_list.append(Car(position=Vector2(x, y)))

        # Move left for next grid
        car_start_x -= cols * spacing + grid_spacing

    # --- Bottom row: full, full, half aligned to vans
    bottom_car_grids = [
        {'cols': full_cols},   # rightmost (align with vans)
        {'cols': full_cols},
        {'cols': half_cols}
    ]

    car_start_y = top_y + (car_rows * spacing) + gap
    car_start_x = right_x  # align bottom rightmost grid with vans

    for grid in bottom_car_grids:
        cols = grid['cols']
        for row in range(car_rows):
            for col in range(cols):
                x = car_start_x - col * spacing
                y = car_start_y + row * spacing
                cars_list.append(Car(position=Vector2(x, y)))

        car_start_x -= cols * spacing + grid_spacing

    print(f"Spawned {len(cars_list)} cars")

def spawn_staff(day, available_vans):
    result = []
    entry_point = Vector2(640, -40)
    for i in range(5):
        courier = StaffCourier(f"S_{day}_{i}")

        courier.scene = "SortingArea_Daily"
        if available_vans:
            for van in available_vans:
                if not van.occupied:
                    courier.assigned_vehicle = van
                    van.occupied = True
                    van.driver = courier
                    break
        result.append(courier)
    return result

def spawn_subcon(day, available_cars):
    result = []
    entry_point = Vector2(640, -40)
    for i in range(3):
        courier = SubconCourier(f"SC_{day}_{i}")
        courier.scene = "SortingArea_Daily"
        if available_cars:
            for car in available_cars:
                if not car.occupied:
                    courier.assigned_vehicle = car
                    car.occupied = True
                    car.driver = courier
                    break
        result.append(courier)
    return result

def spawn_truck(sorting_area, cycle_name):
    start_y = 300  # Vertical lane the truck uses to enter
    return Truck(sorting_area=sorting_area, start_y=start_y, cycle_name=cycle_name)

def spawn_houses(houses_list):
    houses_list.clear()
    
    col_spacing = 42  # Horizontal spacing between columns
    row_spacing = 30  # Vertical spacing between rows

    right_x = SCREEN_WIDTH - 30
    top_y = 25

    house_cols = 25
    house_rows = 20

    house_start_x = right_x
    house_start_y = top_y

    for row in range(house_rows):
        for col in range(house_cols):
            x = house_start_x - col * col_spacing
            y = house_start_y + row * row_spacing
            house = House()
            house.position = Vector2(x, y)
            houses_list.append(house)

    print(f"Spawned {len(houses_list)} houses")