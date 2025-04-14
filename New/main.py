from queue import Queue  # Import Queue for managing courier queuing at box piles
from Courier import Courier  # Import the Courier class
import globals  # Import shared global variables and constants
import time  # For managing simulation timing
import box_pile  # Import the BoxPile class/module
from random import Random  # Random number generation (used for shipment sizes)

isRunning = True  # Flag to keep the simulation running
currTime = time.time()  # Capture the current wall-clock time for simulation timing

# Function to calculate cost (currently unused due to early return)
def calculateCost():
    return  # This immediately ends the function — the logic below is not run
    globals.NO_STAFF * globals.STAFF_MONTHLY_PAY//20 * 20 + \  # Intended cost calc (commented out)
    (globals.NO_FAILED_DELIVERY_SUBCON + globals.NO_SUCCESSFUL_DELIVERY_SUBCON) * globals.SUBCON_PER_STOP_PAY

# Function to create three phase setups (morning, afternoon, reset), based on whether it's peak or non-peak
def setPhase(peak):
    if len(globals.boxPiles)<2:  # Sanity check to ensure boxPiles are initialized
        raise Exception("global.boxPiles Not Initialised")  # Error if not

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
        Random.randint(
            amshipmentmin[i],
            amshipmentmax[i]) 
        for i in range(len(globals.boxPiles))
    ]

    # Generate randomized afternoon shipment volumes per pile
    PM = [
        Random.randint(
            pmshipmentmin[i],
            pmshipmentmax[i]) 
        for i in range(len(globals.boxPiles))
    ]

    # Find max and min shipment volume across all peak and non-peak sets
    maxship = max(
        globals.PEAK_SHIPMENT_MAX_AM + globals.PEAK_SHIPMENT_MAX_PM,
        globals.NONPEAK_SHIPMENT_MAX_AM + globals.NONPEAK_SHIPMENT_MAX_PM
    )

    minship = min(
        globals.NONPEAK_SHIPMENT_MIN_AM + globals.NONPEAK_SHIPMENT_MAX_PM,
        globals.PEAK_SHIPMENT_MIN_PM + globals.PEAK_SHIPMENT_MIN_AM
    )

    # Scale number of NPI and SUBCON couriers based on demand from AM shipments
    globals.NO_NPI = (globals.SUBCON_MAX - globals.SUBCON_MIN) * (AM[0] - minship)/(maxship - minship)
    globals.NO_SUBCON = (globals.SUBCON_MAX - globals.SUBCON_MIN) * (AM[1] - minship)/(maxship - minship)

    # Define a nested function factory that returns an initializer function
    def thing(load):
        # Function to initialize couriers and apply shipment load to piles
        def initialise(load):
            globals.couriers = []  # Reset all couriers

            # Spawn STAFF couriers
            for i in range(globals.NO_STAFF):
                globals.couriers.append(Courier(i, globals.Jobs.STAFF))

            # Spawn SUB_CON couriers
            for i in range(globals.NO_SUBCON):
                globals.couriers.append(Courier(i, globals.Jobs.SUB_CON))

            # Spawn NPI couriers
            for i in range(globals.NO_NPI):
                globals.couriers.append(Courier(i, globals.Jobs.NPI))

            # Distribute shipment load across boxPiles
            for i in range(len(load)):
                globals.boxPiles[i].box_count += load[i]

        return initialise  # Return the nested initializer function

    # Return three initializer functions: morning, afternoon, reset
    return thing(AM), thing(PM), thing([0,0])

# --- Initialization Section ---

# Instantiate 5 STAFF couriers and add them to the globals list
for i in range(5):
    globals.couriers.append(Courier(i, globals.Jobs.STAFF))

# Create 2 BoxPiles (index 0 and 1) with cooldowns 6–9s and initial stock of 40
for i in range(2):
    globals.boxPiles.append(box_pile.BoxPile(i, 6, 9, 40))

# --- Main Simulation Loop ---
while (isRunning):  # Run loop while simulation is active
    currTime = time.time()  # Get current frame time (for frame pacing)

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
