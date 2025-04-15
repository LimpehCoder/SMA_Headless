import globals
import pandas as pd
import matplotlib.pyplot as plt
from Courier import Statuses

def log_daily_delivery_stats():
    # Append current day's delivery stats to the master list
    globals.daily_delivery_stats.append({
        "day": globals.day,
        "staff_success": globals.NO_SUCCESSFUL_DELIVERY_STAFF,
        "staff_fail": globals.NO_FAILED_DELIVERY_STAFF,
        "subcon_success": globals.NO_SUCCESSFUL_DELIVERY_SUBCON,
        "subcon_fail": globals.NO_FAILED_DELIVERY_SUBCON,
        "npi_success": globals.NO_SUCCESSFUL_DELIVERY_NPI,
        "npi_fail": globals.NO_FAILED_DELIVERY_NPI,
    })

    # Reset the counters for the next day
    globals.NO_SUCCESSFUL_DELIVERY_STAFF = 0
    globals.NO_FAILED_DELIVERY_STAFF = 0
    globals.NO_SUCCESSFUL_DELIVERY_SUBCON = 0
    globals.NO_FAILED_DELIVERY_SUBCON = 0
    globals.NO_SUCCESSFUL_DELIVERY_NPI = 0
    globals.NO_FAILED_DELIVERY_NPI = 0

def plot_daily_delivery_summary():
    # Convert the daily delivery log to a DataFrame
    df = pd.DataFrame(globals.daily_delivery_stats)

    if df.empty:
        print("No delivery data available.")
        return

    df.set_index("day", inplace=True)

    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.25
    x = df.index

    # Plot grouped bars for each courier type
    ax.bar(x - width, df["staff_success"], width, label="Staff Success", color="#4caf50")
    ax.bar(x - width, df["staff_fail"], width, bottom=df["staff_success"], label="Staff Fail", color="#c62828")

    ax.bar(x, df["subcon_success"], width, label="Subcon Success", color="#2196f3")
    ax.bar(x, df["subcon_fail"], width, bottom=df["subcon_success"], label="Subcon Fail", color="#e53935")

    ax.bar(x + width, df["npi_success"], width, label="NPI Success", color="#ff9800")
    ax.bar(x + width, df["npi_fail"], width, bottom=df["npi_success"], label="NPI Fail", color="#d32f2f")

    ax.set_xlabel("Day")
    ax.set_ylabel("Deliveries")
    ax.set_title("Daily Successful & Failed Deliveries by Courier Type")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

def log_daily_cost():
    # 1. Staff daily pay
    staff_cost = globals.NO_STAFF * (globals.STAFF_MONTHLY_PAY // 20)

    # 2. Subcon stop pay
    subcon_cost = (globals.NO_FAILED_DELIVERY_SUBCON + globals.NO_SUCCESSFUL_DELIVERY_SUBCON) * globals.SUBCON_PER_STOP_PAY

    # 3. NPI stop pay
    npi_cost = (globals.NO_FAILED_DELIVERY_NPI + globals.NO_SUCCESSFUL_DELIVERY_NPI) * globals.SUBCON_PER_STOP_PAY

    # 4. Idle van penalty
    idle_van_count = max(globals.VAN_COUNT - globals.NO_STAFF, 0)
    van_cost = idle_van_count * 100

    # Save daily breakdown
    globals.daily_cost_stats.append({
        "day": globals.day,
        "staff_cost": staff_cost,
        "subcon_cost": subcon_cost,
        "npi_cost": npi_cost,
        "van_cost": van_cost
    })

    # Reset VAN_COST if needed
    globals.VAN_COST = 0

def plot_daily_cost_summary():
    df = pd.DataFrame(globals.daily_cost_stats)
    if df.empty:
        print("No cost data to plot.")
        return

    df.set_index("day", inplace=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.2
    x = df.index

    ax.bar(x - 1.5*width, df["staff_cost"], width, label="Staff Salary", color="#4caf50")
    ax.bar(x - 0.5*width, df["subcon_cost"], width, label="Subcon Stops", color="#2196f3")
    ax.bar(x + 0.5*width, df["npi_cost"], width, label="NPI Stops", color="#ff9800")
    ax.bar(x + 1.5*width, df["van_cost"], width, label="Idle Vans", color="#c62828")

    ax.set_xlabel("Day")
    ax.set_ylabel("Cost ($)")
    ax.set_title("Daily Cost Breakdown")
    ax.legend()
    plt.tight_layout()
    plt.show()

from collections import Counter

def log_end_of_day_statuses():
    # Count how many couriers ended in each state
    state_names = [courier.state.name for courier in globals.couriers]
    counts = Counter(state_names)

    # Build a clean dict of status counts for the day
    status_record = {"day": globals.day}
    for status in [status.name for status in Statuses]:
        status_record[status.lower()] = counts.get(status, 0)

    globals.daily_status_counts.append(status_record)


def plot_end_of_day_statuses():
    df = pd.DataFrame(globals.daily_status_counts)
    if df.empty:
        print("No status data to plot.")
        return

    df.set_index("day", inplace=True)

    # Get all possible status columns (excluding 'day')
    status_cols = [col for col in df.columns]

    # Plot as stacked bar chart
    ax = df[status_cols].plot(
        kind="bar",
        stacked=True,
        figsize=(12, 6),
        colormap="tab20"
    )
    ax.set_title("Courier Status Distribution at End of Day")
    ax.set_xlabel("Day")
    ax.set_ylabel("Number of Couriers")
    ax.legend(title="Status", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

