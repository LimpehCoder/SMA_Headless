from queue import Queue  # Import Queue for managing courier queuing at box piles
from Courier import Courier, Statuses  # Import the Courier class
import globals  # Import shared global variables and constants
import time  # For managing simulation timing
import box_pile  # Import the BoxPile class/module
import random  # Random number generation (used for shipment sizes)

isRunning = True  # Flag to keep the simulation running
currTime = time.time()  # Capture the current wall-clock time for simulation timing

# Function to calculate cost (currently unused due to early return)
def calculateCost():
    globals.NO_STAFF * globals.STAFF_MONTHLY_PAY//20 * 20 + \
    (globals.NO_FAILED_DELIVERY_SUBCON + globals.NO_SUCCESSFUL_DELIVERY_SUBCON) * globals.SUBCON_PER_STOP_PAY
    return

# Function to create three phase setups (morning, afternoon, reset), based on whether it's peak or non-peak
def setPhase(peak):
    if globals.is_NPI:
        if len(globals.boxPiles)<2:  # Sanity check to ensure boxPiles are initialized
            raise Exception("global.boxPiles Not Initialised")  # Error if not
    else:
        if len(globals.boxPiles)<1:
            raise Exception("global.boxPiles Not Initialised")

    # Assign shipment max/min based on PEAK as default
    amshipmentmax = globals.PEAK_SHIPMENT_MAX_AM
    amshipmentmin = globals.PEAK_SHIPMENT_MIN_AM
    pmshipmentmax = globals.PEAK_SHIPMENT_MAX_PM
    pmshipmentmin = globals.PEAK_SHIPMENT_MIN_PM

    # If this is a NON-PEAK phase, override with non-peak shipment settings
    if peak:
        amshipmentmax = globals.NONPEAK_SHIPMENT_MAX_AM
        amshipmentmin = globals.NONPEAK_SHIPMENT_MIN_AM
        pmshipmentmax = globals.NONPEAK_SHIPMENT_MAX_PM
        pmshipmentmin = globals.NONPEAK_SHIPMENT_MIN_PM

    # Generate randomized morning shipment volumes per pile
    AM = [
        random.randint(
            amshipmentmin[i],
            amshipmentmax[i]) 
        for i in range(len(globals.boxPiles))
    ]

    # Generate randomized afternoon shipment volumes per pile
    PM = [
        random.randint(
            pmshipmentmin[i],
            pmshipmentmax[i]) 
        for i in range(len(globals.boxPiles))
    ]

    # Find max and min shipment volume across all peak and non-peak sets
    # Flatten and get the max and min from all four lists
    maxship = max(
        max(globals.PEAK_SHIPMENT_MAX_AM),
        max(globals.PEAK_SHIPMENT_MAX_PM),
        max(globals.NONPEAK_SHIPMENT_MAX_AM),
        max(globals.NONPEAK_SHIPMENT_MAX_PM)
        )

    minship = min(
        min(globals.PEAK_SHIPMENT_MIN_AM),
        min(globals.PEAK_SHIPMENT_MIN_PM),
        min(globals.NONPEAK_SHIPMENT_MIN_AM),
        min(globals.NONPEAK_SHIPMENT_MIN_PM)
        )

    # Scale number of NPI and SUBCON couriers based on demand from AM shipments
    globals.NO_SUBCON = (globals.SUBCON_MAX - globals.SUBCON_MIN) * (AM[0] - minship)/(maxship - minship)
    if globals.is_NPI:
        globals.NO_NPI = (globals.SUBCON_MAX - globals.SUBCON_MIN) * (AM[0] - minship)/(maxship - minship)

    # Define a nested function factory that returns an initializer function
    def thing(load):
        # Function to initialize couriers and apply shipment load to piles
        def initialise():
            globals.couriers = []  # Reset all couriers

            # Spawn STAFF couriers
            for i in range(globals.NO_STAFF):
                globals.couriers.append(Courier(i, globals.Jobs.STAFF))

            # Spawn SUB_CON couriers
            for i in range(int(globals.NO_SUBCON)):
                globals.couriers.append(Courier(i, globals.Jobs.SUB_CON))
            if globals.is_NPI:
            # Spawn NPI couriers
                for i in range(int(globals.NO_NPI)):
                    globals.couriers.append(Courier(i, globals.Jobs.NPI))

            # Distribute shipment load across boxPiles
            for i in range(len(load)):
                pile_index = i if len(globals.boxPiles) > 1 else 0  # Always redirect to pile 0 if only one exists
                globals.boxPiles[pile_index].box_count += load[i]

        return initialise  # Return the nested initializer function

    # Return three initializer functions: morning, afternoon, reset
    return thing(AM), thing(PM), thing([0,0])

def endofDay():
    if globals.format_clock() == "22:00:00":
        for courier in globals.couriers:
            total_boxes=courier.carryingBoxes + courier.loadedBoxes
            if total_boxes > 0:
                # If the courier has boxes, they will be returned to the box pile
                globals.boxPiles[0].box_count += total_boxes
                courier.loadedBoxes = 0
                courier.carryingBoxes = 0
                print(f"Courier {courier.id} returned {total_boxes} boxes to box pile {courier.job.value}.")
                courier._setState(Statuses.DESPAWNING)
        globals.couriers.clear()
        globals.recall_triggered = True
        print("End of day reached. Triggering recalls.")
        print(f"Staff had {globals.NO_SUCCESSFUL_DELIVERY_STAFF} successful deliveries and {globals.NO_FAILED_DELIVERY_STAFF} failed deliveries.")
        print(f"Subcon had {globals.NO_SUCCESSFUL_DELIVERY_SUBCON} successful deliveries and {globals.NO_FAILED_DELIVERY_SUBCON} failed deliveries.")
        globals.NO_SUCCESSFUL_DELIVERY_STAFF,globals.NO_FAILED_DELIVERY_STAFF,globals.NO_SUCCESSFUL_DELIVERY_SUBCON,globals.NO_FAILED_DELIVERY_SUBCON = 0,0,0,0

# --- Initialization Section ---

# Instantiate 5 STAFF couriers and add them to the globals list
for i in range(5):
    globals.couriers.append(Courier(i, globals.Jobs.STAFF))

if globals.is_NPI:
    for i in range(2):
        globals.boxPiles.append(box_pile.BoxPile(i, 6, 9, 0))
# Create 2 BoxPiles (index 0 and 1) with cooldowns 6–9s and initial stock of 40
else:
    for i in range(1):
        globals.boxPiles.append(box_pile.BoxPile(i, 6, 9, 0))

# Set whether current day is peak or non-peak
if globals.is_peak:
    set_morning, set_afternoon, set_reset = setPhase(peak=True)
else:
    set_morning, set_afternoon, set_reset = setPhase(peak=False)

# --- Main Simulation Loop ---
while (isRunning):  # Run loop while simulation is active
    currTime = time.time()  # Get current frame time (for frame pacing)
    globals.clock = (globals.clock + 1) % 86400  # 86400 seconds in a day
    if globals.clock == 0:
        globals.day += 1
    # Setup once at the beginning of each shift
    if globals.format_clock() == "08:00:00" and globals.phase_initialised != "MORNING":
        set_morning()
        globals.phase_initialised = "MORNING"
        globals.shift = globals.Shifts.MORNING
        print("Morning phase initialized.")

    elif globals.format_clock() == "13:00:00" and globals.phase_initialised != "AFTERNOON":
        set_afternoon()
        globals.phase_initialised = "AFTERNOON"
        globals.shift = globals.Shifts.AFTERNOON
        print("Afternoon phase initialized.")

    elif globals.format_clock() == "18:00:00" and globals.phase_initialised != "OVERTIME":
        set_reset()
        globals.phase_initialised = "OVERTIME"
        globals.shift = globals.Shifts.OVERTIME
        print("Reset phase initialized.")

    elif globals.format_clock() == "22:00:00":
        endofDay()
    
    elif globals.format_clock() == "07:00:00":
        globals.recall_triggered = False
        # Reset couriers at the start of the day

    if globals.format_clock() < "22:00:00" and globals.format_clock() > "07:00:00":
        # --- Update Phase: Courier Logic ---
        for courier in globals.couriers:
            courier.update()  # Let each courier update its state

        # --- Update Phase: BoxPile Logic ---
        for boxPile in globals.boxPiles:
            boxPile.update()  # Let each pile update (pickup, restock, etc.)

    # --- Frame Pacing ---
    # globals.dt = time.time() - currTime  # Uncomment to enable real-time pacing

    while (globals.dt < 1/60):  # Enforce 60 FPS timing
        globals.dt = time.time() - currTime  # Wait until enough time has passed for next frame
    
    if globals.day == 120:
        isRunning = False