import globals
import pandas as pd
import matplotlib.pyplot as plt
from Courier import Statuses
from collections import Counter

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
    staff_success = df["staff_success"]
    staff_fail = df["staff_fail"]
    subcon_success = df["subcon_success"]
    subcon_fail = df["subcon_fail"]
    npi_success = df["npi_success"]
    npi_fail = df["npi_fail"]

    staff_total = staff_success + staff_fail
    subcon_total = subcon_success + subcon_fail
    npi_total = npi_success + npi_fail

    # Plotting bars
    bars = []
    bars.append(ax.bar(x - width, staff_success, width, label="Staff Success", color="#4caf50"))
    bars.append(ax.bar(x - width, staff_fail, width, bottom=staff_success, label="Staff Fail", color="#c62828"))

    bars.append(ax.bar(x, subcon_success, width, label="Subcon Success", color="#2196f3"))
    bars.append(ax.bar(x, subcon_fail, width, bottom=subcon_success, label="Subcon Fail", color="#e53935"))

    bars.append(ax.bar(x + width, npi_success, width, label="NPI Success", color="#ff9800"))
    bars.append(ax.bar(x + width, npi_fail, width, bottom=npi_success, label="NPI Fail", color="#d32f2f"))

    # Annotate each segment with its percentage
    for i, day in enumerate(df.index):
        # Staff
        total = staff_total.loc[day]
        if total > 0:
            ax.text(x[i] - width, staff_success.loc[day] / 2,
                    f"{(staff_success.loc[day] / total * 100):.0f}%", ha="center", va="center", color="white", fontsize=9)
            ax.text(x[i] - width, staff_success.loc[day] + staff_fail.loc[day] / 2,
                    f"{(staff_fail.loc[day] / total * 100):.0f}%", ha="center", va="center", color="white", fontsize=9)

        # Subcon
        total = subcon_total.loc[day]
        if total > 0:
            ax.text(x[i], subcon_success.loc[day] / 2,
                    f"{(subcon_success.loc[day] / total * 100):.0f}%", ha="center", va="center", color="white", fontsize=9)
            ax.text(x[i], subcon_success.loc[day] + subcon_fail.loc[day] / 2,
                    f"{(subcon_fail.loc[day] / total * 100):.0f}%", ha="center", va="center", color="white", fontsize=9)

        # NPI
        total = npi_total.loc[day]
        if total > 0:
            ax.text(x[i] + width, npi_success.loc[day] / 2,
                    f"{(npi_success.loc[day] / total * 100):.0f}%", ha="center", va="center", color="black", fontsize=9)
            ax.text(x[i] + width, npi_success.loc[day] + npi_fail.loc[day] / 2,
                    f"{(npi_fail.loc[day] / total * 100):.0f}%", ha="center", va="center", color="white", fontsize=9)

    ax.set_xlabel("Day")
    ax.set_ylabel("Deliveries")
    ax.set_title("Daily Successful & Failed Deliveries by Courier Type")
    ax.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

def log_daily_cost():
    # 1. Staff is paid every 20 days (on day 1, 21, 41, ...)
    staff_cost = 4000 if (globals.day - 1) % 20 == 0 else 0

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

    # Plot each category of cost
    staff_bars = ax.bar(x - 1.5*width, df["staff_cost"], width, label="Staff Salary", color="#4caf50")
    subcon_bars = ax.bar(x - 0.5*width, df["subcon_cost"], width, label="Subcon Stops", color="#2196f3")
    npi_bars = ax.bar(x + 0.5*width, df["npi_cost"], width, label="NPI Stops", color="#ff9800")
    van_bars = ax.bar(x + 1.5*width, df["van_cost"], width, label="Idle Vans", color="#c62828")

    # Annotate each bar with its height (i.e., cost)
    for bars in [staff_bars, subcon_bars, npi_bars, van_bars]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"${int(height)}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # Offset slightly above the bar
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Day")
    ax.set_ylabel("Cost ($)")
    ax.set_title("Daily Cost Breakdown")
    ax.legend()
    plt.tight_layout()
    plt.show()

def log_end_of_shift_statuses():
    # Count courier statuses at the end of the current shift
    state_names = [courier.state.name for courier in globals.couriers]
    counts = Counter(state_names)

    # Build a record with day + shift
    status_record = {
        "day": globals.day,
        "shift": globals.shift.name if globals.shift else "UNKNOWN"
    }

    # Include counts for each known status
    for status in [status.name for status in Statuses]:
        status_record[status.lower()] = counts.get(status, 0)

    globals.daily_status_counts.append(status_record)

def plot_end_of_shift_statuses():
    df = pd.DataFrame(globals.daily_status_counts)
    if df.empty:
        print("No status data to plot.")
        return

    # Combine day and shift into a single label for x-axis
    df["label"] = df["day"].astype(str) + " - " + df["shift"]

    # Set label as index
    df.set_index("label", inplace=True)

    # Get only the status columns (exclude 'day' and 'shift')
    status_cols = [col for col in df.columns if col not in ["day", "shift"]]

    # Plot stacked bar chart
    ax = df[status_cols].plot(
        kind="bar",
        stacked=True,
        figsize=(14, 6),
        colormap="tab20"
    )

    # Annotate each stacked segment with percentage
    for i, label in enumerate(df.index):
        total = df.loc[label, status_cols].sum()
        if total == 0:
            continue

        y_offset = 0
        for col in status_cols:
            value = df.at[label, col]
            if value == 0:
                continue
            percent = value / total * 100
            ax.text(i, y_offset + value / 2, f"{percent:.0f}%", ha='center', va='center', color='white', fontsize=8)
            y_offset += value

    ax.set_title("Courier Status Distribution at End of Each Shift")
    ax.set_xlabel("Day - Shift")
    ax.set_ylabel("Number of Couriers")
    ax.legend(title="Status", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def log_shift_leftover_boxes():
    shift_name = globals.shift.name if globals.shift else "UNKNOWN"
    day = globals.day

    total_boxes = sum(pile.box_count for pile in globals.boxPiles)

    # Optional: breakdown by pile
    pile_data = {f"pile_{i}": pile.box_count for i, pile in enumerate(globals.boxPiles)}

    # Log shift-level leftover count
    log_entry = {
        "day": day,
        "shift": shift_name,
        "total_boxes": total_boxes,
        **pile_data
    }

    globals.leftover_boxes_log.append(log_entry)

def plot_leftover_boxes_by_shift():
    df = pd.DataFrame(globals.leftover_boxes_log)
    if df.empty:
        print("No box log data to plot.")
        return

    pivot_df = df.pivot(index="day", columns="shift", values="total_boxes").fillna(0)

    ax = pivot_df.plot(kind="bar", figsize=(12, 6), width=0.7)

    # Annotate each bar with the box count
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f"{int(height)}",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # Slightly above the bar
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)

    ax.set_title("Leftover Boxes at End of Each Shift")
    ax.set_xlabel("Day")
    ax.set_ylabel("Box Count")
    ax.legend(title="Shift")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

def log_daily_route_metrics():
    from collections import defaultdict
    day_stats = defaultdict(lambda: {"routes": 0, "stops": 0, "time": 0.0})

    for route in globals.route_stats:
        if route["day"] != globals.day:
            continue
        key = route["job"].lower()
        day_stats[key]["routes"] += 1
        day_stats[key]["stops"] += route["stops"]
        day_stats[key]["time"] += route["route_time"]

    # Store per-day summary
    globals.daily_route_summary.append({
        "day": globals.day,
        "staff_spr": day_stats["staff"]["stops"] / day_stats["staff"]["routes"] if day_stats["staff"]["routes"] else 0,
        "subcon_spr": day_stats["sub_con"]["stops"] / day_stats["sub_con"]["routes"] if day_stats["sub_con"]["routes"] else 0,
        "npi_spr": day_stats["npi"]["stops"] / day_stats["npi"]["routes"] if day_stats["npi"]["routes"] else 0,

        "staff_sph": day_stats["staff"]["stops"] / (day_stats["staff"]["time"]/3600) if day_stats["staff"]["time"] else 0,
        "subcon_sph": day_stats["sub_con"]["stops"] / (day_stats["sub_con"]["time"]/3600) if day_stats["sub_con"]["time"] else 0,
        "npi_sph": day_stats["npi"]["stops"] / (day_stats["npi"]["time"]/3600) if day_stats["npi"]["time"] else 0,
    })

def get_courier_route_dataframe(filename="courier_routes.csv"):
    if not globals.courier_route_stats:
        print("No courier route data available.")
        return pd.DataFrame()

    df = pd.DataFrame(globals.courier_route_stats)
    df = df[["day", "shift", "courier_id", "job", "stops", "route_time", "spr", "sporh"]]
    print(df)
    df.to_csv(filename, index=False)
    return