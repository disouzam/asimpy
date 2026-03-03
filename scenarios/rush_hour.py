"""Rush Hour Displacement: individual avoidance of congestion shifts but never ends it."""

import random
import statistics
import sys

import altair as alt
import polars as pl

# Road and commuter parameters
N_COMMUTERS = 200  # total commuters
N_SLOTS = 30  # departure time slots (e.g., each = 2 minutes)
PREFERRED_SLOT = 15  # ideal departure slot index
ROAD_CAPACITY = 20  # max commuters the road handles comfortably per slot
OVERLOAD_DELAY = 3.0  # extra delay per commuter above capacity
BASE_DELAY = 1.0  # delay when below capacity
N_DAYS = 40  # number of days to simulate
SHIFT_PROB = 0.3  # probability a commuter shifts after a bad day
SEED = 42


def simulate_day(departure_slots: list[int]) -> dict[int, float]:
    """
    Run one day's commute: count commuters per slot and compute
    travel time for each slot based on crowding.
    Returns a dict mapping slot -> travel_time.
    """
    counts: dict[int, int] = {}
    for s in departure_slots:
        counts[s] = counts.get(s, 0) + 1

    travel_time: dict[int, float] = {}
    for slot, count in counts.items():
        if count <= ROAD_CAPACITY:
            travel_time[slot] = BASE_DELAY
        else:
            overflow = count - ROAD_CAPACITY
            travel_time[slot] = BASE_DELAY + OVERLOAD_DELAY * overflow / ROAD_CAPACITY
    return travel_time


def update_slots(
    departure_slots: list[int], travel_times: dict[int, float], rng: random.Random
) -> list[int]:
    """
    Each commuter considers shifting +/-1 slot if their current slot is
    congested. They shift with probability SHIFT_PROB toward a less busy
    neighbour if that neighbour has lower travel time.
    """
    new_slots = departure_slots[:]
    for i, s in enumerate(departure_slots):
        my_delay = travel_times.get(s, BASE_DELAY)
        # Check neighbours
        candidates = []
        if s > 0:
            candidates.append(s - 1)
        if s < N_SLOTS - 1:
            candidates.append(s + 1)
        better = [c for c in candidates if travel_times.get(c, BASE_DELAY) < my_delay]
        if better and rng.random() < SHIFT_PROB:
            new_slots[i] = rng.choice(better)
    return new_slots


def slot_distribution(slots: list[int]) -> list[int]:
    counts = [0] * N_SLOTS
    for s in slots:
        counts[s] += 1
    return counts


rng = random.Random(SEED)

# Initialise: commuters start clustered near the preferred slot with some spread
departure_slots = [
    max(0, min(N_SLOTS - 1, PREFERRED_SLOT + round(rng.gauss(0, 2))))
    for _ in range(N_COMMUTERS)
]

rows = []
for day in range(N_DAYS):
    travel_times = simulate_day(departure_slots)
    mean_delay = statistics.mean(
        travel_times.get(s, BASE_DELAY) for s in departure_slots
    )
    dist = slot_distribution(departure_slots)
    max_count = max(dist)
    rows.append({"day": day + 1, "mean_delay": mean_delay, "max_slot_count": max_count})
    departure_slots = update_slots(departure_slots, travel_times, rng)

df = pl.DataFrame(rows)

final_dist = slot_distribution(departure_slots)
peak_slot = max(range(N_SLOTS), key=lambda s: final_dist[s])

print("Rush Hour Displacement Simulation")
print(f"  {N_COMMUTERS} commuters, {N_SLOTS} slots, road capacity {ROAD_CAPACITY}/slot")
print(f"  Overload delay: {OVERLOAD_DELAY}x base delay per unit above capacity")
print()
print(df)
print()
print(f"Initial peak slot: {PREFERRED_SLOT}")
print(
    f"Final peak slot:   {peak_slot} ({'same' if peak_slot == PREFERRED_SLOT else 'shifted'})"
)
print()
print("Observation: the rush-hour peak flattens and shifts but does not disappear.")

chart = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=alt.X("day:Q", title="Day"),
        y=alt.Y("mean_delay:Q", title="Mean travel delay"),
        tooltip=["day:Q", "mean_delay:Q", "max_slot_count:Q"],
    )
    .properties(title="Rush Hour Displacement: Mean Delay Over Time")
)
chart.save(sys.argv[1])
