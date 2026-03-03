"""Arrival Process: random independent events produce exponential gaps.

The Poisson process is the mathematical model for "things happening at random
at a constant average rate."  Two equivalent signatures identify it: gaps
between consecutive events follow an exponential distribution, and the count
of events in any window follows a Poisson distribution.
"""

import math
import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process

SIM_TIME = 10_000
ARRIVAL_RATE = 2.0  # λ: mean arrivals per time unit
WINDOW = 1.0  # width of each counting window
SEED = 42


class ArrivalSource(Process):
    """Generates arrivals at a Poisson rate and records inter-arrival gaps."""

    def init(self, rate: float, gaps: list[float]):
        self.rate = rate
        self.gaps = gaps

    async def run(self):
        while True:
            gap = random.expovariate(self.rate)
            await self.timeout(gap)
            self.gaps.append(gap)


def collect_gaps(rate: float = ARRIVAL_RATE, seed: int = SEED) -> list[float]:
    random.seed(seed)
    gaps: list[float] = []
    env = Environment()
    ArrivalSource(env, rate, gaps)
    env.run(until=SIM_TIME)
    return gaps


gaps = collect_gaps()
mean_gap = statistics.mean(gaps)
stdev_gap = statistics.stdev(gaps)

df_summary = pl.DataFrame(
    [
        {"quantity": "target λ", "value": ARRIVAL_RATE},
        {"quantity": "measured λ (1/mean)", "value": round(1.0 / mean_gap, 5)},
        {"quantity": "mean inter-arrival", "value": round(mean_gap, 5)},
        {"quantity": "theory mean (1/λ)", "value": round(1.0 / ARRIVAL_RATE, 5)},
        {"quantity": "stdev inter-arrival", "value": round(stdev_gap, 5)},
        {"quantity": "theory stdev (1/λ)", "value": round(1.0 / ARRIVAL_RATE, 5)},
    ]
)

# Count arrivals in successive windows and compare to Poisson(λ·WINDOW) theory
n_windows = int(SIM_TIME / WINDOW)
window_counts: list[int] = [0] * n_windows
t = 0.0
for g in gaps:
    t += g
    w = int(t / WINDOW)
    if w < n_windows:
        window_counts[w] += 1

max_k = max(window_counts)
freq: dict[int, int] = {}
for c in window_counts:
    freq[c] = freq.get(c, 0) + 1

lam_w = ARRIVAL_RATE * WINDOW  # expected count per window
dist_rows = []
for k in range(max_k + 1):
    observed = freq.get(k, 0) / n_windows
    theory = (lam_w**k) * math.exp(-lam_w) / math.factorial(k)
    dist_rows.append(
        {"k": k, "observed": round(observed, 5), "Poisson theory": round(theory, 5)}
    )

df_dist = pl.DataFrame(dist_rows)

print("Arrival Process: Poisson Arrivals and Exponential Gaps")
print(
    f"  λ={ARRIVAL_RATE}, window={WINDOW}, {len(gaps)} arrivals in {SIM_TIME} time units"
)
print()
print(df_summary)
print()
print(f"Count distribution in windows of width {WINDOW}:")
print(df_dist)

df_plot = df_dist.unpivot(
    on=["observed", "Poisson theory"],
    index="k",
    variable_name="source",
    value_name="probability",
)
chart = (
    alt.Chart(df_plot)
    .mark_bar(opacity=0.8)
    .encode(
        x=alt.X("k:O", title=f"Arrivals per window (width {WINDOW})"),
        y=alt.Y("probability:Q", title="Probability"),
        color=alt.Color("source:N", title="Series"),
        xOffset="source:N",
        tooltip=["k:O", "source:N", "probability:Q"],
    )
    .properties(title=f"Arrival Counts: Observed vs. Poisson(λ={ARRIVAL_RATE})")
)
chart.save(sys.argv[1])
