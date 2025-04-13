from enum import Enum
import random
import globals
import box_pile

class Statuses(Enum):
    IDLING = 0
    WALKING = 1 # walking to queue
    SORTING = 2 # queuing
    MOVING = 3 # moving to van
    LOADING = 4 # loading van
    DRIVING = 5
    DELIVERING = 6
    RETURNING = 7
    DESPAWNING = 8

delays = [
    [0, 0], # idling
    [4, 8], # walking
    [0, 0], # queuing
    [6, 9], # moving
    [3, 5], # loading
    [1, 1], # driving
    [5, 5], # delivering
    [globals.RETURN_MIN_TIMING, globals.RETURN_MAX_TIMING], # returning
    [0, 0], # despawning
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
    maxAttempts: int
    attempts: int
    
    CARRYING_CAPACITY: int = 5
    # VEHICLE_CAPACITY: int = globals.VAN_CAP_MIN
    rng = random.Random()

    def reset(self):
        self._setState(Statuses.WALKING)
        self.carryingBoxes = 0
        self.loadedBoxes = 0
        self.shldCountdown = True
        self.timer = 0
        self.isAlive = True

    def __init__(self, id: int, job: globals.Jobs):
        self.id = id
        self.job = job
        self.reset()
    
    def _setState(self, state: Statuses):
        self.state = state
        print(f"entering {state.name}")
        if delays[self.state.value][0] == 0 and delays[self.state.value][1] == 0:
            self.shldCountdown = False
        else:
            self.timer = self.rng.uniform(delays[self.state.value][0], delays[self.state.value][1])
            self.shldCountdown = True
    
    def _hasAllReachedCap():
        for courier in globals.couriers:
            if courier.loadedBoxes < globals.VAN_CAP_MIN:
                return False
        return True
        
    def update(self):
        if not self.shldCountdown:
            return

        self.timer -= globals.dt
        if(self.timer==globals.DAY_LENGTH):
            self.isAlive = False
        if (self.timer > 0):
            return
        
        if (self.state == Statuses.IDLING):
            print("exited idling")
            self._setState(Statuses.WALKING)

        elif (self.state == Statuses.WALKING):
            result = False
            if self.job == globals.Jobs.STAFF:
                if globals.shift == globals.Shifts.OVERTIME:
                    result = globals.boxPiles[self.rng.randint(0, 1)].try_enter_queue(self)
                else:
                    result = globals.boxPiles[0].try_enter_queue(self)
            else:
                result = globals.boxPiles[self.job.value].try_enter_queue(self)

            if result:
                self._setState(Statuses.SORTING)
            elif self.loadedBoxes > 0:
                self._setState(Statuses.MOVING)
            else:
                self._setState(Statuses.IDLING)
            
            print(f"result: {result}")
            print("exited walking")

        elif (self.state == Statuses.SORTING):
            print("exited sorting")

        elif (self.state == Statuses.MOVING):
            self._setState(Statuses.LOADING)
            print("exited moving")

        elif (self.state == Statuses.LOADING):
            print("exited loading")

            self.loadedBoxes += self.carryingBoxes
            self.carryingBoxes = 0

            targetQueues = []

            if self.job == globals.Jobs.STAFF:
                if globals.shift == globals.Shifts.OVERTIME:
                    targetQueues.append(0)
                    targetQueues.append(1)
                else:
                    targetQueues.append(0)
            else:
                targetQueues.append(self.job.value)

            areAllBoxCountsZero = True
            print(f"size: {len(globals.boxPiles)}")
            for queue in targetQueues:
                print(f"queue : {queue}")
                if globals.boxPiles[queue].box_count != 0:
                    areAllBoxCountsZero = False
                    break;

            print(f"courier {self.id} has {self.loadedBoxes} boxes")

            if self.loadedBoxes == globals.VAN_CAP_MAX or areAllBoxCountsZero:
                self._setState(Statuses.DRIVING)
                self.maxAttempts = self.loadedBoxes
                self.attempts = 0
            elif self.loadedBoxes < globals.VAN_CAP_MIN:
                self._setState(Statuses.WALKING)
            elif self.loadedBoxes == globals.VAN_CAP_MIN and box_pile.BoxPile.min_loaded_count == globals.VAN_CAP_MIN:
                self._setState(Statuses.WALKING)
            elif self.loadedBoxes >=globals.VAN_CAP_MIN and box_pile.BoxPile.min_loaded_count >= globals.VAN_CAP_MIN:
                self._setState(Statuses.DRIVING)
                self.maxAttempts = self.loadedBoxes
                self.attempts = 0
            else:
               raise "you messed up"

        elif (self.state == Statuses.DRIVING):
            self._setState(Statuses.DELIVERING)
            print("exited driving")

        elif (self.state == Statuses.DELIVERING):
            if self.loadedBoxes > 0 and self.attempts < self.maxAttempts:
                if self.rng.uniform(0, 1) > globals.AT_HOME_CHANCE:
                    if self.job == globals.Jobs.STAFF:
                        self.loadedBoxes -= 1
                    elif self.rng.uniform(0, 1) > globals.IS_BLIND_CHANCE:
                        self.loadedBoxes -= 1

                self.attempts += 1
                self._setState(Statuses.DRIVING)
            else:
                self._setState(Statuses.RETURNING)
            print("exited delivering")

        elif (self.state == Statuses.RETURNING):
            self._setState(Statuses.IDLING)
            globals.boxPiles[self.rng.randint(0, 1)].box_count += self.loadedBoxes
            self._setState(Statuses.WALKING)
            print("exited returning")
            print(f"courier {self.id} has {self.loadedBoxes} boxes left")

        elif (self.state == Statuses.DESPAWNING):
            pass

        else:
            print("Unknown status")

    def leaveQueue(self):
        self._setState(Statuses.MOVING)
        return self.loadedBoxes
        