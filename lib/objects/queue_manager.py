import warnings
from enum import Enum
from pygame.math import Vector2
from queue import Queue, Empty, Full


class Directions(Enum):
    # unit vectors
    LEFT = Vector2(-1, 0)
    RIGHT = Vector2(1, 0)
    UP = Vector2(0, -1)
    DOWN = Vector2(0, 1)


def add_courier_to_queue(queue: Queue, courier):
    try:
        queue.put_nowait(courier)
    except Full:
        print("queue is full")


def remove_first_from_queue(queue: Queue):
    try:
        return queue.get_nowait()
    except Empty:
        print("queue is empty")


class QueueManager:
    def __init__(self, position, max_size, spacing=40):
        self.position = position
        self.maxsize = max_size
        self.spacing = spacing

        self.queues = {direction: Queue(maxsize=0) for direction in Directions}
        self.queue_positions = {direction: [] for direction in Directions}

    def generate_queue(self, direction: Directions | None):
        self.queues[direction] = Queue(maxsize=self.maxsize)
        self.queue_positions[direction] = self.generate_positions(direction)

    def generate_positions(self, direction):
        offset = direction.value * self.spacing
        return [
            self.position + offset * (i + 1)
            for i in range(self.maxsize)
        ]

    def get_queue(self, direction: Directions):
        if self.queues[direction].maxsize == 0:
            print(f"there is no queue for {direction}, try generating one!")
            return None
        return self.queues[direction]

    def add_courier_to_direction(self, courier, direction: Directions):
        try:
            queue = self.get_queue(direction)
            if queue is not None:
                queue.put_nowait(courier)

            with queue.mutex:
                try:
                    index = list(queue.queue).index(courier)
                    courier.target_position = self.queue_positions[direction][index]
                except ValueError:
                    warnings.warn("this courier didn't get added to the queue... shouldn't happen")
                    return
        except Full:
            print("queue is full")

    def remove_first_from_direction(self, direction: Directions):
        try:
            queue = self.get_queue(direction)
            if queue is not None:
                queue.get_nowait()

            with queue.mutex:
                try:
                    for i, courier in enumerate(queue.queue):
                        if courier:
                            courier.target_position = self.queue_positions[direction][i]
                except ValueError:
                    warnings.warn("this courier didn't get removed")

        except Empty:
            print("no one is in this queue!")
            return None

    def remove_courier_from_direction(self, courier, direction: Directions):
        try:
            queue = self.get_queue(direction)
            if not queue:
                return

            with queue.mutex:
                try:
                    index = list(queue.queue).index(courier)
                    if index == 0:
                        self.remove_first_from_direction(direction)
                    else:
                        print("cannot remove courier not first in line")
                except ValueError:
                    warnings.warn("this courier didn't get removed")

        except Empty:
            print("queue is empty")
            return