import queue
import random
import Courier
import globals

class BoxPile:
  min_loaded_count = 0
  def __init__(self, min_cooldown: float, max_cooldown: float, initial_pile: int, max_length=69):
    self.box_count = initial_pile
    self.min_cooldown = min_cooldown
    self.max_cooldown = max_cooldown
    self.timer = 0.0
    self.max_length = max_length
    self.queue = queue.Queue(maxsize=self.max_length)


  def try_enter_queue(self, courier: Courier):
    try:
      if self.box_count <= self.queue.qsize() * courier.CARRYING_CAPACITY:
        print("no boxes bro")
        return False
      self.queue.put_nowait(courier)
      print(f"[{globals.dt}] courier with id {courier.id} entered queue")
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
        
  def make_courier_pickup(self, courier: Courier):
    # carrying = courier.carryingBoxes
    to_top_up = min(self.box_count, courier.CARRYING_CAPACITY)
    
    courier.carryingBoxes += to_top_up
    self.box_count -= to_top_up
    num_carrying = courier.leaveQueue()
    if num_carrying < BoxPile.min_loaded_count:
      BoxPile.min_loaded_count = num_carrying