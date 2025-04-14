import queue
import random
import Courier
import globals

class BoxPile:
  min_loaded_count = 0
  def __init__(self, index: int, min_cooldown: float, max_cooldown: float, initial_pile: int, max_length=100):
    self.index = index
    self.box_count = initial_pile
    self.min_cooldown = min_cooldown
    self.max_cooldown = max_cooldown
    self.timer = 0.0
    self.max_length = max_length
    self.queue = queue.Queue(maxsize=self.max_length)
    self.restock_interval = 60          # Restock every 60 seconds
    self.restock_timer = self.restock_interval
    self.max_capacity = 10000             # Optional cap on pile size
    self.last_restocked_shift = None 

    # Restock amounts per shift
    self.restock_amounts = {
      globals.Shifts.MORNING: 20,
      globals.Shifts.AFTERNOON: 10,
      globals.Shifts.OVERTIME: 0  # No restock during overtime
    }



  def try_enter_queue(self, courier: Courier):
    try:
      if self.box_count <= self.queue.qsize() * courier.CARRYING_CAPACITY:
        print("no boxes bro")
        return False
      self.queue.put_nowait(courier)
      print(f"Courier with id {courier.id} entered queue at time {globals.format_clock()}")
      return True
    except queue.Full:
      print("queue full bro")
      return False

  def update(self):
    try:
      self.timer-=globals.dt
      if self.timer <= 0:
        self.make_courier_pickup(self.queue.get_nowait())
        if self.box_count > 0:
          self.timer = random.uniform(self.min_cooldown, self.max_cooldown)    
    except queue.Empty:
      pass
    # --- Handle restocking on shift change ---
    current_shift = globals.shift

    if current_shift in [globals.Shifts.MORNING, globals.Shifts.AFTERNOON]:
        if self.last_restocked_shift != current_shift:
            # Determine restock amount based on shift and peak status
            if globals.is_peak:
                if current_shift == globals.Shifts.MORNING:
                    min_amt = globals.PEAK_SHIPMENT_MIN_AM[self.index]
                    max_amt = globals.PEAK_SHIPMENT_MAX_AM[self.index]
                else:  # AFTERNOON
                    min_amt = globals.PEAK_SHIPMENT_MIN_PM[self.index]
                    max_amt = globals.PEAK_SHIPMENT_MAX_PM[self.index]
            else:
                if current_shift == globals.Shifts.MORNING:
                    min_amt = globals.NONPEAK_SHIPMENT_MIN_AM[self.index]
                    max_amt = globals.NONPEAK_SHIPMENT_MAX_AM[self.index]
                else:  # AFTERNOON
                    min_amt = globals.NONPEAK_SHIPMENT_MIN_PM[self.index]
                    max_amt = globals.NONPEAK_SHIPMENT_MAX_PM[self.index]

            # Restock once at start of shift
            restock_amt = random.randint(min_amt, max_amt)
            self.box_count = min(self.box_count + restock_amt, self.max_capacity)
            self.last_restocked_shift = current_shift

            print(f"[{globals.format_day()} {globals.format_clock()}] Shift: {current_shift.name} — Pile {self.index} restocked {restock_amt} boxes (total: {self.box_count})")

        
  def make_courier_pickup(self, courier: Courier):
    # carrying = courier.carryingBoxes
    to_top_up = min(self.box_count, courier.CARRYING_CAPACITY)
    
    courier.carryingBoxes += to_top_up
    self.box_count -= to_top_up
    num_carrying = courier.leaveQueue()
    if num_carrying < BoxPile.min_loaded_count:
      BoxPile.min_loaded_count = num_carrying