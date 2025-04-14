from enum import Enum  # For defining courier states
import random  # For randomized delays and outcomes
import globals  # Import global variables like clock, shift, box piles, etc.
import box_pile  # To reference the BoxPile class

class Statuses(Enum):
    IDLING = 0         # Not doing anything
    WALKING = 1        # Walking to a box pile queue
    SORTING = 2        # Waiting in the queue to pick up boxes
    MOVING = 3         # Moving to van after picking up boxes
    LOADING = 4        # Loading boxes into the van
    DRIVING = 5        # Driving to delivery locations
    DELIVERING = 6     # Attempting deliveries
    RETURNING = 7      # Returning after delivery
    DESPAWNING = 8     # End-of-day shutdown

delays = [
    [0, 0],                             # IDLING — no delay
    [4, 8],                             # WALKING — 4 to 8 seconds
    [0, 0],                             # SORTING — handled by pile, no internal delay
    [6, 9],                             # MOVING — to the van
    [3, 5],                             # LOADING — load into vehicle
    [1, 1],                             # DRIVING — fixed travel time
    [5, 5],                             # DELIVERING — attempt takes time
    [globals.RETURN_MIN_TIMING, globals.RETURN_MAX_TIMING],  # RETURNING — variable travel back time
    [0, 0],                             # DESPAWNING — instant
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
    attempts: int
    
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
        print(f"{self.job} courier {self.id} is entering {state.name} at date-time: {globals.format_day()} {globals.format_clock()} on day {globals.day}")
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
        # If there's no countdown to run (state with no delay), do nothing
        if not self.shldCountdown:
            return

        # Decrease timer based on elapsed simulation time
        self.timer -= globals.dt

        # Unused? If the timer hits a full day length, kill the courier
        if self.timer == globals.DAY_LENGTH:
            self.isAlive = False

        # If timer isn't finished, wait
        if self.timer > 0:
            return

        # === State Machine ===
        # Each block below represents a courier state and what happens when the timer expires

        if self.state == Statuses.IDLING:
            # Immediately transition back to walking and try to queue again
            print(f"{self.job} courier {self.id} has exited idling at {globals.format_day()} {globals.format_clock()}")
            self._setState(Statuses.WALKING)

        elif self.state == Statuses.WALKING:
            # Attempt to enter the queue based on courier type and shift
            result = False
            if self.job == globals.Jobs.STAFF:
                if globals.shift == globals.Shifts.OVERTIME:
                    result = globals.boxPiles[self.rng.randint(0, len(globals.boxPiles) - 1)].try_enter_queue(self)
                else:
                    result = globals.boxPiles[0].try_enter_queue(self)
            else:
                result = globals.boxPiles[self.job.value].try_enter_queue(self)

            # Transition based on queue success and loaded status
            if result:
                self._setState(Statuses.SORTING)
            elif self.loadedBoxes > 0:
                self._setState(Statuses.MOVING)
            else:
                self._setState(Statuses.IDLING)

            print(f"result: {result}")
            print(f"{self.job} courier {self.id} has exited walking at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.SORTING:
            # Sorting is handled by the box pile — no internal logic on exit
            print(f"{self.job} courier {self.id} has exited sorting at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.MOVING:
            # Proceed to load boxes into van
            self._setState(Statuses.LOADING)
            print(f"{self.job} courier {self.id} has exited moving at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.LOADING:
            # Transfer carried boxes into van
            print(f"{self.job} courier {self.id} has exited loading at {globals.format_day()} {globals.format_clock()}")
            self.loadedBoxes += self.carryingBoxes
            self.carryingBoxes = 0

            # Determine which box queues to check based on job and shift
            targetQueues = []
            if self.job == globals.Jobs.STAFF:
                if globals.shift == globals.Shifts.OVERTIME:
                    targetQueues.extend([0, 1])
                else:
                    targetQueues.append(0)
            else:
                targetQueues.append(self.job.value)

            # Check if all target piles are empty
            areAllBoxCountsZero = all(globals.boxPiles[q].box_count == 0 for q in targetQueues)

            print(f"{self.job} courier {self.id} has {self.loadedBoxes} boxes at {globals.format_day()} {globals.format_clock()}")

            # Determine if the courier should drive or go back to pick up more
            if self.loadedBoxes >= globals.VAN_CAP_MAX or areAllBoxCountsZero:
                print(f"[LOADING] {self.job} courier {self.id} is proceeding to DRIVING because loadedBoxes = {self.loadedBoxes} (>= VAN_CAP_MAX) or all queues empty.")
                self._setState(Statuses.DRIVING)
                self.maxAttempts = self.loadedBoxes
                self.attempts = 0
            elif self.loadedBoxes < globals.VAN_CAP_MIN:
                print(f"[LOADING] {self.job} courier {self.id} is going back to WALKING because loadedBoxes = {self.loadedBoxes} (< VAN_CAP_MIN).")
                self._setState(Statuses.WALKING)
            elif self.loadedBoxes == globals.VAN_CAP_MIN and box_pile.BoxPile.min_loaded_count == globals.VAN_CAP_MIN:
                print(f"[LOADING] {self.job} courier {self.id} is going back to WALKING because loadedBoxes == VAN_CAP_MIN and min_loaded_count == VAN_CAP_MIN.")
                self._setState(Statuses.WALKING)
            elif self.loadedBoxes >= globals.VAN_CAP_MIN and box_pile.BoxPile.min_loaded_count >= globals.VAN_CAP_MIN:
                print(f"[LOADING] {self.job} courier {self.id} is proceeding to DRIVING because both loadedBoxes ({self.loadedBoxes}) and min_loaded_count are >= VAN_CAP_MIN.")
                self._setState(Statuses.DRIVING)
                self.maxAttempts = self.loadedBoxes
                self.attempts = 0
            elif self.loadedBoxes >= globals.VAN_CAP_MIN and self.loadedBoxes <= globals.VAN_CAP_MAX and box_pile.BoxPile.min_loaded_count <= globals.VAN_CAP_MIN:
                print(f"[LOADING] {self.job} courier {self.id} is proceeding to DRIVING because loadedBoxes = {self.loadedBoxes} is within range and min_loaded_count <= VAN_CAP_MIN.")
                self._setState(Statuses.DRIVING)
            else:
                raise "you messed up"

        elif self.state == Statuses.DRIVING:
            # Arrived at destination, begin delivery attempt
            self._setState(Statuses.DELIVERING)
            print(f"{self.job} courier {self.id} has exited driving at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.DELIVERING:
            # Try to deliver boxes one-by-one
            if self.loadedBoxes > 0 and self.attempts < self.maxAttempts:
                # Attempt delivery: may or may not succeed depending on courier type
                if self.rng.uniform(0, 1) > globals.AT_HOME_CHANCE:
                    if self.job == globals.Jobs.STAFF:
                        self.loadedBoxes -= 1
                    elif self.job == globals.Jobs.SUB_CON:
                        if self.rng.uniform(0, 1) > globals.IS_BLIND_CHANCE:
                            self.loadedBoxes -= 1
                self.attempts += 1
                self._setState(Statuses.DRIVING)  # Go back for the next stop

            else:
                # All delivery attempts completed — calculate and record success/failure
                if self.job == globals.Jobs.STAFF:
                    success = round(self.maxAttempts * globals.AT_HOME_CHANCE)
                    fail = self.maxAttempts - success
                    globals.NO_SUCCESSFUL_DELIVERY_STAFF += success
                    globals.NO_FAILED_DELIVERY_STAFF += fail

                elif self.job == globals.Jobs.SUB_CON:
                    success = round(self.maxAttempts * globals.AT_HOME_CHANCE * (1 - globals.IS_BLIND_CHANCE))
                    fail = self.maxAttempts - success
                    globals.NO_SUCCESSFUL_DELIVERY_SUBCON += success
                    globals.NO_FAILED_DELIVERY_SUBCON += fail

                self._setState(Statuses.RETURNING)  # Move on to return phase

            print(f"{self.job} courier {self.id} has exited delivering at {globals.format_day()} {globals.format_clock()}")


        elif self.state == Statuses.RETURNING:
            # Return any leftover boxes to a random box pile and restart
            self._setState(Statuses.IDLING)
            globals.boxPiles[self.rng.randint(0, 1)].box_count += self.loadedBoxes
            self._setState(Statuses.WALKING)

            print(f"{self.job} courier {self.id} has exited returning at {globals.format_day()} {globals.format_clock()}")
            print(f"{self.job} courier {self.id} has {self.loadedBoxes} boxes left at {globals.format_day()} {globals.format_clock()}")

        elif self.state == Statuses.DESPAWNING:
            # No updates for despawned couriers
            pass
        else:
            print("Unknown status")  # Fallback for unexpected state

    def leaveQueue(self):
        self._setState(Statuses.MOVING)  # Transition to MOVING
        return self.loadedBoxes  # Report how many are loaded