from enum import Enum  # For defining courier states
import random  # For randomized delays and outcomes
import globals  # Import global variables like clock, shift, box piles, etc.
import box_pile  # To reference the BoxPile class

class Statuses(Enum):
    IDLING = 0         # Not doing anything
    WALKING = 1        # Walking to a box pile
    SORTING = 2        # Picking up boxes
    MOVING = 3         # Moving to van after picking up boxes
    LOADING = 4        # Loading boxes into the van
    DRIVING = 5        # Driving to delivery locations
    DELIVERING = 6     # Attempting deliveries
    RETURNING = 7      # Returning after delivery
    DESPAWNING = 8     # End-of-day shutdown
    RESTING = 9      # Resting between shifts

delays = [
    [0, 0],                             # IDLING — no delay
    [30, 60],                             # WALKING — 4 to 8 seconds
    [60, 120],                             # SORTING — handled by pile, no internal delay
    [120, 180],                             # MOVING — to the van
    [120, 180],                             # LOADING — load into vehicle
    [globals.DRIVING_MIN_TIMING, globals.DRIVING_MAX_TIMING],                             # DRIVING — fixed travel time
    [globals.DELIVERING_MIN_TIMING, globals.DELIVERING_MAX_TIMING],                             # DELIVERING — attempt takes time
    [globals.RETURN_MIN_TIMING, globals.RETURN_MAX_TIMING],  # RETURNING — variable travel back time
    [0, 0],                             # DESPAWNING — instant
    [0,0]
    
]


class Courier:
    id: int
    state: Statuses
    timer: float
    carryingBoxes: int
    loadedBoxes: int
    shldCountdown: bool 
    hasJob: bool
    isAlive: bool
    job: globals.Jobs
    stopCount: int # number of times a stop is made
    maxAttempts: int = 50
    attempts: int = 0
    
    CARRYING_CAPACITY: int = 5
    # VEHICLE_CAPACITY: int = globals.VAN_CAP_MIN
    rng = random.Random()

    def reset(self):
        self._setState(Statuses.WALKING)  # Start in WALKING state
        self.carryingBoxes = 0  # Empty hands
        self.loadedBoxes = 0  # Empty van
        self.shldCountdown = True  # Enable countdown
        self.timer = 0  # Reset timer
        self.isAlive = True  # Set alive status

    def __init__(self, id: int, job: globals.Jobs):
        self.id = id  # Assign ID
        self.job = job  # Assign job type
        self.reset()  # Initialize values

    def _setState(self, state: Statuses):
        self.state = state  # Assign state
        #print(f"{self.job} courier {self.id} is entering {state.name} at date-time: {globals.format_day()} {globals.format_clock()} on day {globals.day}")
        if delays[self.state.value][0] == 0 and delays[self.state.value][1] == 0:
            self.shldCountdown = False  # No timer needed
        else:
            self.timer = self.rng.uniform(delays[self.state.value][0], delays[self.state.value][1])  # Set countdown
            self.shldCountdown = True  # Enable countdown

    
    def _hasAllReachedCap():
        for courier in globals.couriers:
            if courier.loadedBoxes < globals.VAN_CAP_MIN:
                return False  # Someone is under capacity
        return True  # All ready
        
    def update(self):
        # Determine assigned pile index
        if self.job == globals.Jobs.NPI:
            pile_index = 1 if len(globals.boxPiles) > 1 else 0
        else:
            pile_index = 0  # STAFF and default go to pile 0
        
        # If there's no countdown to run (state with no delay), do nothing
        if not self.shldCountdown:
            return

        # Decrease timer based on elapsed simulation time
        self.timer -= 1

        # Unused? If the timer hits a full day length, kill the courier
        #if self.timer == globals.DAY_LENGTH:
        #    self.isAlive = False

        # If timer isn't finished, wait
        if self.timer > 0:
            return

        # === State Machine ===
        # Each block below represents a courier state and what happens when the timer expires

        if self.state == Statuses.IDLING:
            # Check if boxes are available in assigned pile
            if globals.boxPiles[pile_index].box_count > 0:
               # print(f"{self.job} courier {self.id} is exiting IDLING — boxes are available at pile {pile_index}")
                self._setState(Statuses.WALKING)
          #  else:
             #   print(f"{self.job} courier {self.id} remains IDLING — pile {pile_index} is empty")

        elif self.state == Statuses.WALKING:
            if globals.boxPiles[pile_index].box_count > 0:
               # print(f"{self.job} courier {self.id} is exiting WALKING — heading to SORTING at pile {pile_index}")
                self._setState(Statuses.SORTING)
            else:
                # Still nothing there — loop back to IDLING
                self._setState(Statuses.IDLING)
             #   print(f"{self.job} courier {self.id} is exiting WALKING — pile {pile_index} is empty, going IDLE")

        elif self.state == Statuses.SORTING:
            # Pick up boxes
            globals.boxPiles[pile_index].make_courier_pickup(self)
         #   print(f"{self.job} courier {self.id} has exited SORTING and is now MOVING")
            self._setState(Statuses.MOVING)

        elif self.state == Statuses.MOVING:
            # Proceed to load boxes into van
            self._setState(Statuses.LOADING)
         #   print(f"{self.job} courier {self.id} has exited moving at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.LOADING:
            # Transfer carried boxes into van
          #  print(f"{self.job} courier {self.id} has exited loading at {globals.format_day()} {globals.format_clock()}")
            self.loadedBoxes += self.carryingBoxes
            self.carryingBoxes = 0

            # Determine which box queues to check based on job and shift
            
            # Check if all target piles are empty
            if globals.boxPiles[pile_index].box_count == 0:
                areAllBoxCountsZero = True
            else:
                areAllBoxCountsZero = False
        #    print(f"{self.job} courier {self.id} has {self.loadedBoxes} boxes at {globals.format_day()} {globals.format_clock()}")

            # Determine if the courier should drive or go back to pick up more
            if self.loadedBoxes >= globals.VAN_CAP_MAX or areAllBoxCountsZero:
             #  print(f"[LOADING] {self.job} courier {self.id} is proceeding to DRIVING because loadedBoxes = {self.loadedBoxes} (>= VAN_CAP_MAX) or all queues empty.")
                self._setState(Statuses.DRIVING)
                self.maxAttempts = self.loadedBoxes
                self.attempts = 0
            elif self.loadedBoxes < globals.VAN_CAP_MIN:
              #  print(f"[LOADING] {self.job} courier {self.id} is going back to WALKING because loadedBoxes = {self.loadedBoxes} (< VAN_CAP_MIN).")
                self._setState(Statuses.WALKING)
            elif self.loadedBoxes == globals.VAN_CAP_MIN and box_pile.BoxPile.min_loaded_count == globals.VAN_CAP_MIN:
               # print(f"[LOADING] {self.job} courier {self.id} is going back to WALKING because loadedBoxes == VAN_CAP_MIN and min_loaded_count == VAN_CAP_MIN.")
                self._setState(Statuses.WALKING)
            elif self.loadedBoxes >= globals.VAN_CAP_MIN and box_pile.BoxPile.min_loaded_count >= globals.VAN_CAP_MIN:
              #  print(f"[LOADING] {self.job} courier {self.id} is proceeding to DRIVING because both loadedBoxes ({self.loadedBoxes}) and min_loaded_count are >= VAN_CAP_MIN.")
                self._setState(Statuses.DRIVING)
                self.maxAttempts = self.loadedBoxes
                self.attempts = 0
            elif self.loadedBoxes >= globals.VAN_CAP_MIN and self.loadedBoxes <= globals.VAN_CAP_MAX and box_pile.BoxPile.min_loaded_count <= globals.VAN_CAP_MIN:
               # print(f"[LOADING] {self.job} courier {self.id} is proceeding to DRIVING because loadedBoxes = {self.loadedBoxes} is within range and min_loaded_count <= VAN_CAP_MIN.")
                self._setState(Statuses.DRIVING)
            else:
                raise "you messed up"

        elif self.state == Statuses.DRIVING:
            # Arrived at destination, begin delivery attempt
            self._setState(Statuses.DELIVERING)
           # print(f"{self.job} courier {self.id} has exited driving at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.DELIVERING:
            # Try to deliver boxes one-by-one
            if self.loadedBoxes > 0 and self.attempts < self.maxAttempts:
                if self.job == globals.Jobs.STAFF:
                    toDeliver=int(random.uniform(1,5))
                    if toDeliver>self.loadedBoxes:
                        toDeliver=self.loadedBoxes
                    if self.rng.uniform(0, 1) > globals.NOT_HOME_CHANCE:
                        self.loadedBoxes -= toDeliver
                        globals.NO_SUCCESSFUL_DELIVERY_STAFF +=toDeliver
                    else: 
                        globals.NO_FAILED_DELIVERY_STAFF +=toDeliver
                elif self.job == globals.Jobs.SUB_CON:
                    toDeliver=int(random.uniform(1,5))
                    if toDeliver>self.loadedBoxes:
                        toDeliver=self.loadedBoxes
                    if self.rng.uniform(0, 1) > globals.NOT_HOME_CHANCE:
                        if self.rng.uniform(0,1) > globals.IS_BLIND_CHANCE:
                            self.loadedBoxes -= toDeliver
                            globals.NO_SUCCESSFUL_DELIVERY_SUBCON +=toDeliver
                        else:
                            globals.NO_FAILED_DELIVERY_SUBCON +=toDeliver
                elif self.job == globals.Jobs.NPI:
                    toDeliver=int(random.uniform(1,5))
                    if toDeliver>self.loadedBoxes:
                        toDeliver=self.loadedBoxes
                    if self.rng.uniform(0, 1) > globals.NOT_HOME_CHANCE:
                        if self.rng.uniform(0,1) > globals.IS_BLIND_CHANCE*1.2:
                            self.loadedBoxes -= toDeliver
                            globals.NO_SUCCESSFUL_DELIVERY_NPI +=toDeliver
                        else:
                            globals.NO_FAILED_DELIVERY_NPI +=toDeliver
                                            
                self.attempts += 1
                #print(f"{self.job} courier {self.id} has {self.loadedBoxes} boxes left at {globals.format_day()} {globals.format_clock()}")
                self._setState(Statuses.DRIVING)  # Go back for the next stop

            else:
                self._setState(Statuses.RETURNING)  # Move on to return phase
             #   print(f"{self.job} courier {self.id} has completed deliveries with {self.loadedBoxes} boxes left at {globals.format_day()} {globals.format_clock()}")

           # print(f"{self.job} courier {self.id} has exited delivering at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.RETURNING:
            # Return any leftover boxes to a random box pile and restart
            globals.boxPiles[pile_index].box_count += self.loadedBoxes
            self._setState(Statuses.RESTING)

        #    print(f"{self.job} courier {self.id} has exited returning at {globals.format_day()} {globals.format_clock()}")
#            print(f"{self.job} courier {self.id} has {self.loadedBoxes} boxes left at {globals.format_day()} {globals.format_clock()}")
        elif self.state == Statuses.RESTING:
            print(f"{self.job} courier {self.id} is resting")

        elif self.state == Statuses.DESPAWNING:
            # No updates for despawned couriers
            pass
        else:
            print("Unknown status")  # Fallback for unexpected state

    def leaveQueue(self):
        self._setState(Statuses.MOVING)  # Transition to MOVING
        return self.loadedBoxes  # Report how many are loaded