from queue import Queue
from Courier import Courier
import globals
import time
import box_pile
from random import Random

isRunning = True
currTime = time.time()

def calculateCost():
    return 
    globals.NO_STAFF * globals.STAFF_MONTHLY_PAY//20 * 20 + \
    (globals.NO_FAILED_DELIVERY_SUBCON + globals.NO_SUCCESSFUL_DELIVERY_SUBCON) * globals.SUBCON_PER_STOP_PAY

def setPhase(peak):
    if len(globals.boxPiles)<2:
        raise Exception("global.boxPiles Not Initialised")
    amshipmentmax = globals.PEAK_SHIPMENT_MAX_AM
    amshipmentmin = globals.PEAK_SHIPMENT_MIN_AM
    pmshipmentmax = globals.PEAK_SHIPMENT_MAX_PM
    pmshipmentmin = globals.PEAK_SHIPMENT_MIN_PM
    if peak:
        amshipmentmax = globals.NONPEAK_SHIPMENT_MAX_AM
        amshipmentmin = globals.NONPEAK_SHIPMENT_MIN_AM
        pmshipmentmax = globals.NONPEAK_SHIPMENT_MAX_PM
        pmshipmentmin = globals.NONPEAK_SHIPMENT_MIN_PM
    AM = [
        Random.randint(
            amshipmentmin[i],
            amshipmentmax[i]) 
        for i in range(len(globals.boxPiles))
    ]
    PM = [
        Random.randint(
            pmshipmentmin[i],
            pmshipmentmax[i]) 
        for i in range(len(globals.boxPiles))
    ]
    maxship = max(
        globals.PEAK_SHIPMENT_MAX_AM + globals.PEAK_SHIPMENT_MAX_PM,
        globals.NONPEAK_SHIPMENT_MAX_AM + globals.NONPEAK_SHIPMENT_MAX_PM
    )
    minship = min(
        globals.NONPEAK_SHIPMENT_MIN_AM + globals.NONPEAK_SHIPMENT_MAX_PM,
        globals.PEAK_SHIPMENT_MIN_PM + globals.PEAK_SHIPMENT_MIN_AM
    )
    globals.NO_NPI = (globals.SUBCON_MAX - globals.SUBCON_MIN) * (AM[0] - minship)/(maxship - minship)
    globals.NO_SUBCON = (globals.SUBCON_MAX - globals.SUBCON_MIN) * (AM[1] - minship)/(maxship - minship)
    def thing(load):
        def initialise(load):
            globals.couriers = []
            for i in range(globals.NO_STAFF):
                globals.couriers.append(Courier(i, globals.Jobs.STAFF))
            for i in range(globals.NO_SUBCON):
                globals.couriers.append(Courier(i, globals.Jobs.SUB_CON))
            for i in range(globals.NO_NPI):
                globals.couriers.append(Courier(i, globals.Jobs.NPI))
            for i in range(len(load)):
                globals.boxPiles[i].box_count += load[i]
        return initialise
    return thing(AM), thing(PM), thing([0,0])

# init
for i in range(5):
    globals.couriers.append(Courier(i, globals.Jobs.STAFF))

for i in range(2):
    globals.boxPiles.append(box_pile.BoxPile(6, 9, 40))

while (isRunning):
    currTime = time.time()

    for courier in globals.couriers:
        courier.update()
    for boxPile in globals.boxPiles:
        boxPile.update()

    # keep at 60 fps
    globals.dt = time.time() - currTime # comment this line to run sim instantly (without random delays)
    while (globals.dt < 1/60):
        globals.dt = time.time() - currTime
