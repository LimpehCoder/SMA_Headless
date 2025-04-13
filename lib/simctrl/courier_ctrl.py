import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from spawner import spawn_vans, spawn_cars, spawn_staff, spawn_subcon, spawn_truck, CYCLE_TIMES
from pygame.math import Vector2
from spawner import spawn_staff, spawn_subcon
from objects.courier import StaffCourier, SubconCourier
from objects.queue_manager import Directions

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

class CourierController:
    def __init__(self, sorting_area, carpark, courier_type, scene_manager):
        self.sorting_area = sorting_area
        self.carpark = carpark
        self.courier_type = courier_type  # "Courier_Staff" or "Courier_Subcon"
        self.spawned = False
        self.last_day = None
        self.queue_index = None
        self.queue_type = None
        self.scene_manager = scene_manager  # Add this line

        # State definitions
        self.states = {
            "OFF_WORK": self._off_work,
            "REPORTING": self._reporting,
            "IDLE": self._idle,
            "MOVE_TO_QUEUE": self._move_to_queue,
            "QUEUING": self._queuing,
            "SORTING": self._sorting,
            "LOADING": self._sorting,  # Same as sorting for now
            "DELIVERING": self._delivering  # Optional future state
        }

    @staticmethod
    def initialize_idle_grids():
        StaffCourier.idle_grid = [
            Vector2(SCREEN_WIDTH - 50 - col * 40, 80 + row * 40)
            for row in range(3) for col in range(10)
        ]
        SubconCourier.idle_grid = [
            Vector2(SCREEN_WIDTH - 50 - col * 40, SCREEN_HEIGHT - 200 + row * 40)
            for row in range(3) for col in range(10)
        ]

    def reset_daily_state(self, day):
        self.spawned = False
        self.sorting_area.spawned_today = False
        self.last_day = day

    def spawn(self, day):
        raise NotImplementedError("This method must be implemented by subclasses.")

    def stream_pending(self, dt):
        self.sorting_area.courier_spawn_timer += dt
        if self.sorting_area.pending_couriers and self.sorting_area.courier_spawn_timer >= self.sorting_area.courier_spawn_interval:
            next_courier = self.sorting_area.pending_couriers.pop(0)
            self.sorting_area.couriers.append(next_courier)
            self.sorting_area.courier_spawn_timer = 0

    def report(self, dt, sim_clock):
        hour, minute, day = sim_clock.hour, sim_clock.minute, sim_clock.day

        if hour == 6 and minute == 0 and day != self.last_day:
            self.reset_daily_state(day)
        if hour == 7 and not self.spawned:
            self.spawn(day)
            self.spawned = True
        self.stream_pending(dt)

        for courier in self.sorting_area.couriers:
            if courier.type == self.courier_type:
                self.states.get(courier.status, self._off_work)(courier, dt)

        # Shift all queue rows after all couriers are updated
        self.update_all_queue_rows()

            
    def _off_work(self, courier, dt):
        pass

    def _reporting(self, courier, dt):
        if self._move_towards(courier, courier.idle_position, dt):
            courier.status = "IDLE"

    def _idle(self, courier, dt):
        courier.slot_request_timer += dt  # Accumulate time

        if courier.slot_request_timer >= courier.slot_request_interval:
            success = courier.request_slot(self.sorting_area.box_pile)
            if success:
                courier.slot_request_timer = 0  # Reset timer only on success

    def _move_to_queue(self, courier, dt):
        # Move toward assigned queue slot
        if self._move_towards(courier, courier.target_position, dt):
            courier.status = "QUEUING"

    def _queuing(self, courier, dt):
        pile = self.sorting_area.box_pile
        if courier.queue_type == "R":
            occupied, slots = pile.right_occupied, pile.right_queue_slots
        elif courier.queue_type == "T":
            occupied, slots = pile.top_occupied, pile.top_queue_slots
        elif courier.queue_type == "B":
            occupied, slots = pile.bottom_occupied, pile.bottom_queue_slots
        else:
            return

        # Check if courier is at front of their queue and in position
        if courier.queue_index == 0 and (courier.position - courier.target_position).length() < 5:
            # Attempt to pick up until they have 5 or the pile is empty
            while courier.carrying < 5 and not pile.is_empty():
                courier.pickup_box(pile)

            # If courier is full, leave the queue
            if courier.carrying >= 5:
                courier.status = "SORTING"
                occupied[0] = None
                courier.queue_index = None
                courier.queue_type = None
                self.update_all_queue_rows()
                while courier.carrying > 0:
                    courier.move_to_carpark(current_scene=self.sorting_area, scene_manager=self.scene_manager, dt=dt)

    def _sorting(self, courier, dt):
        if courier.assigned_vehicle:
            courier.target_position = courier.assigned_vehicle.target_position
            if self._move_towards(courier, courier.target_position, dt):
                courier.assigned_vehicle.load_box()
                courier.carrying = 0
                courier.status = "IDLE"

    def _delivering(self, courier, dt):
        pass

    def update_all_queue_rows(self):
        pile = self.sorting_area.box_pile
        if not pile:
            return
        for direction in [Directions.RIGHT, Directions.UP, Directions.DOWN]:
            queue = pile.queue_manager.get_queue(direction)
            slots = pile.queue_manager.queue_positions[direction]

            if queue is None:
                continue  # Skip if queue hasn't been generated

            with queue.mutex:  # To safely iterate over Queue contents
                queue_list = list(queue.queue)

            for i in range(1, len(queue_list)):
                courier = queue_list[i]
                if courier and queue_list[i - 1] is None:
                    # Move courier forward in the queue
                    queue_list[i] = None
                    queue_list[i - 1] = courier
                    courier.queue_index = i - 1
                    courier.target_position = slots[i - 1]
                    print(f"[Global Queue Shift] {courier.id} → {direction.name}{i - 1}")

        # Reassign modified queue
        with queue.mutex:
            queue.queue.clear()
            for item in queue_list:
                if item is not None:
                    queue.queue.append(item)


    def _move_towards(self, courier, target, dt):
        direction = target - courier.position
        if direction.length() < 2:
            courier.position = target
            return True
        direction.normalize_ip()
        courier.position += direction * courier.speed * (dt / 1000.0)
        return False

class StaffController(CourierController):
    def __init__(self, sorting_area, carpark, scene_manager):
        super().__init__(sorting_area, carpark, courier_type="Courier_Staff", scene_manager=scene_manager)

    def spawn(self, day):
        staff = spawn_staff(day, self.carpark.vans)
        for courier in staff:
            courier.status = "REPORTING"
        self.sorting_area.pending_couriers += staff

class SubconController(CourierController):
    def __init__(self, sorting_area, carpark, scene_manager):
        super().__init__(sorting_area, carpark, courier_type="Courier_Subcon", scene_manager=scene_manager)

    def spawn(self, day):
        subcons = spawn_subcon(day, self.carpark.cars)
        for courier in subcons:
            courier.status = "REPORTING"
        self.sorting_area.pending_couriers += subcons