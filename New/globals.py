from enum import Enum

DAY_LENGTH: float = 20
PEAK_SHIPMENT_MIN_AM = [8000, 2000]
PEAK_SHIPMENT_MAX_AM = [10000, 3000]
NONPEAK_SHIPMENT_MIN_AM = [4000, 2000]
NONPEAK_SHIPMENT_MAX_AM = [5000, 3000]
PEAK_SHIPMENT_MIN_PM = [3000,0]
PEAK_SHIPMENT_MAX_PM = [4000,0]
NONPEAK_SHIPMENT_MIN_PM = [1000,0]
NONPEAK_SHIPMENT_MAX_PM = [1500,0]
SUBCON_MIN = 40
SUBCON_MAX = 120
VAN_CAP_MIN = 50
VAN_CAP_MAX = 55
VAN_COUNT = 50
VAN_COST = 0
RETURN_MIN_TIMING = 20*60
RETURN_MAX_TIMING = 40*60
DRIVING_MIN_TIMING = 5*60
DRIVING_MAX_TIMING = 8*60
DELIVERING_MIN_TIMING = 2*60
DELIVERING_MAX_TIMING = 3*60
NO_FAILED_DELIVERY_STAFF: int = 0
NO_FAILED_DELIVERY_SUBCON: int = 0
NO_SUCCESSFUL_DELIVERY_STAFF: int = 0
NO_SUCCESSFUL_DELIVERY_SUBCON: int = 0
NO_FAILED_DELIVERY_NPI: int = 0
NO_SUCCESSFUL_DELIVERY_NPI: int = 0
NOT_HOME_CHANCE: float = 0.2
IS_BLIND_CHANCE: float = 0.2
STAFF_MONTHLY_PAY = 4000
SUBCON_PER_STOP_PAY = 2
NO_STAFF = 50
NO_SUBCON = 40
NO_NPI = 40

phase_initialised = None  # Can be "MORNING", "AFTERNOON", or "OVERTIME"
dt: float = 0
day: int = 1
shift: int = 1
clock: int = 25200  
is_peak: bool = False  # True if peak season, False if non-peak
is_NPI: bool = False  # True if NPI couriers are present, False otherwise
recall_triggered: bool = False  # True if recalls have been triggered, False otherwise

def format_clock() -> str:
    hours = clock // 3600
    minutes = (clock % 3600) // 60
    seconds = clock % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def format_day() -> str:
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    # Only 5-day workweek — wrap every 5 days
    day_index = (day - 1) % 5
    return f"{weekdays[day_index]}"

couriers = []
boxPiles = []

class Jobs(Enum):
    SUB_CON = 0
    NPI = 1
    STAFF = 2

class Shifts(Enum):
    MORNING = 0
    AFTERNOON = 1
    OVERTIME = 2

daily_delivery_stats = []  # Holds one dict per day
daily_cost_stats =[]
daily_status_counts = []  # List of dicts, one per day
