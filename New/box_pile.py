import random
import Courier
import globals


class BoxPile:
  min_loaded_count = 0

  def __init__(self, index: int, min_cooldown: float, max_cooldown: float, initial_pile: int, max_length=1000):
    self.index = index
    self.box_count = initial_pile
    self.min_cooldown = min_cooldown
    self.max_cooldown = max_cooldown
    self.timer = 0.0
    self.max_length = max_length
    self.restock_interval = 60
    self.restock_timer = self.restock_interval
    self.max_capacity = 10000
    self.last_restocked_shift = None

    # Optional: still included in case you use it later
    self.restock_amounts = {
      globals.Shifts.MORNING: 20,
      globals.Shifts.AFTERNOON: 10,
      globals.Shifts.OVERTIME: 0
    }

#  def check_has_boxes(self, courier: Courier):
#    if self.box_count < courier.CARRYING_CAPACITY:
#      print(f"No boxes available for courier {courier.id} at time {globals.format_clock()}")
#      return False
#    return True

  def update(self):
    self.timer -= globals.dt
    if self.timer <= 0:
      # Manually call make_courier_pickup() from courier logic now
      self.timer = random.uniform(self.min_cooldown, self.max_cooldown)

  def make_courier_pickup(self, courier: Courier):
    to_top_up = min(self.box_count, courier.CARRYING_CAPACITY)

    courier.carryingBoxes += to_top_up
    self.box_count -= to_top_up
    num_carrying = courier.leaveQueue()  # Triggers transition to MOVING
    if num_carrying < BoxPile.min_loaded_count:
      BoxPile.min_loaded_count = num_carrying

#    print(f"Courier with id {courier.id} picked up {courier.carryingBoxes} boxes at time {globals.format_clock()}")
#    print(f"Box pile {self.index} has {self.box_count} boxes left at {globals.format_day()} {globals.format_clock()}")