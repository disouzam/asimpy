"""Inspector's Paradox: a random observer almost always arrives during a long gap."""

import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process

SIM_TIME = 100_000
MEAN_HEADWAY = 10.0  # average time between buses
N_PASSENGERS = 20_000  # random-time passengers used for wait estimation
SEED = 42


class BusService(Process):
    """Generates buses and records their arrival times."""

    def init(self, mode: str, bus_arrivals: list):
        self.mode = mode
        self.bus_arrivals = bus_arrivals

    async def run(self):
        while True:
            if self.mode == "regular":
                # Deterministic: perfectly spaced, zero variance
                headway = MEAN_HEADWAY
            elif self.mode == "exponential":
                # Memoryless: headway ~ Exp(1/mean), high variance (CV=1)
                headway = random.expovariate(1.0 / MEAN_HEADWAY)
            elif self.mode == "clustered":
                # Bimodal: buses arrive in bursts (mean=10, high variance)
                headway = 2.0 if random.random() < 0.5 else 18.0
            else:
                raise ValueError(f"Unknown mode: {self.mode}")
            await self.timeout(headway)
            self.bus_arrivals.append(self.now)


def collect_buses(mode: str, seed: int = SEED) -> list[float]:
    random.seed(seed)
    bus_arrivals: list[float] = []
    env = Environment()
    BusService(env, mode, bus_arrivals)
    env.run(until=SIM_TIME)
    return bus_arrivals


def expected_wait(
    bus_arrivals: list[float], n: int = N_PASSENGERS, seed: int = SEED
) -> float:
    """Estimate mean passenger wait by sampling random arrival times."""
    rng = random.Random(seed + 1)
    max_t = bus_arrivals[-1]
    waits: list[float] = []
    for _ in range(n):
        t = rng.uniform(0.0, max_t * 0.95)
        # Find the first bus that arrives after t
        for b in bus_arrivals:
            if b > t:
                waits.append(b - t)
                break
    return statistics.mean(waits) if waits else 0.0


def headway_variance(bus_arrivals: list[float]) -> float:
    headways = [b - a for a, b in zip(bus_arrivals, bus_arrivals[1:])]
    return statistics.variance(headways) if len(headways) > 1 else 0.0


rows = []
naive = MEAN_HEADWAY / 2.0
for mode in ["regular", "exponential", "clustered"]:
    buses = collect_buses(mode)
    var_h = headway_variance(buses)
    mean_w = expected_wait(buses)
    rows.append(
        {
            "mode": mode,
            "var_headway": var_h,
            "mean_wait": mean_w,
            "ratio": mean_w / naive,
        }
    )

df = pl.DataFrame(rows)

mu = MEAN_HEADWAY
var_clustered = 0.5 * (2 - mu) ** 2 + 0.5 * (18 - mu) ** 2

print("Inspector's Paradox")
print(f"  Mean headway: {MEAN_HEADWAY}  =>  naive expected wait = {naive:.1f}")
print()
print(df)
print()
print(
    "The Inspector's Paradox formula: E[wait] = E[headway]/2 + Var[headway] / (2 * E[headway])"
)
print(
    f"  Exponential (Var = E^2 = {mu**2:.1f}): predicted = {mu:.1f}  (= full mean headway!)"
)
print(
    f"  Clustered   (Var = {var_clustered:.1f}):  predicted = {mu / 2 + var_clustered / (2 * mu):.1f}"
)

chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("mode:N", title="Bus schedule type"),
        y=alt.Y("mean_wait:Q", title="Mean passenger wait"),
        color=alt.Color("mode:N", legend=None),
        tooltip=["mode:N", "mean_wait:Q", "ratio:Q"],
    )
    .properties(title="Inspector's Paradox: Mean Wait by Schedule Type")
)
naive_line = (
    alt.Chart(pl.DataFrame({"naive": [naive]}))
    .mark_rule(strokeDash=[4, 4], color="gray")
    .encode(y="naive:Q")
)
(chart + naive_line).save(sys.argv[1])
