"""Priority Starvation: high-priority load can cause low-priority jobs to wait forever.

Demonstrates two effects:
1. Static priority: as hi-priority utilization grows, lo-priority waits diverge.
2. Aging: the server promotes a lo-priority job once it has waited long enough,
   preventing starvation at the cost of occasional hi-priority delay bursts.
"""

import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process, Queue

SIM_TIME = 30_000
SERVICE_RATE_HI = 2.0  # mean service time = 0.5 for hi-priority
SERVICE_RATE_LO = 1.0  # mean service time = 1.0 for lo-priority
ARRIVAL_RATE_LO = 0.2  # rho_lo = 0.2 / 1.0 = 0.20  (fixed)
AGING_THRESHOLD = 15.0  # lo-priority promoted if waiting longer than this
SEED = 42


class StaticPriorityServer(Process):
    """
    Non-preemptive static priority.
    hi_q: holds (arrival_time, service_time) for high-priority jobs.
    lo_q: holds (arrival_time, service_time) for low-priority jobs.
    Always drains hi_q first.
    """

    def init(self, hi_q: Queue, lo_q: Queue, sojourn_hi: list, sojourn_lo: list):
        self.hi_q = hi_q
        self.lo_q = lo_q
        self.sojourn_hi = sojourn_hi
        self.sojourn_lo = sojourn_lo

    async def _serve(self, arrival: float, svc: float, record: list):
        await self.timeout(svc)
        record.append(self.now - arrival)

    async def run(self):
        while True:
            if not self.hi_q.is_empty():
                arrival, svc = await self.hi_q.get()
                await self._serve(arrival, svc, self.sojourn_hi)
            elif not self.lo_q.is_empty():
                arrival, svc = await self.lo_q.get()
                await self._serve(arrival, svc, self.sojourn_lo)
            else:
                await self.timeout(0.01)  # idle: poll briefly


class AgingServer(Process):
    """
    Non-preemptive priority with aging: a lo-priority job that has waited
    longer than AGING_THRESHOLD is promoted ahead of fresh hi-priority jobs.
    """

    def init(self, hi_q: Queue, lo_q: Queue, sojourn_hi: list, sojourn_lo: list):
        self.hi_q = hi_q
        self.lo_q = lo_q
        self.sojourn_hi = sojourn_hi
        self.sojourn_lo = sojourn_lo

    async def run(self):
        while True:
            # Check if oldest lo-priority job has aged past threshold
            lo_aged = (
                not self.lo_q.is_empty()
                and self.now - self.lo_q._items[0][0] >= AGING_THRESHOLD
            )
            if lo_aged:
                arrival, svc = await self.lo_q.get()
                await self.timeout(svc)
                self.sojourn_lo.append(self.now - arrival)
            elif not self.hi_q.is_empty():
                arrival, svc = await self.hi_q.get()
                await self.timeout(svc)
                self.sojourn_hi.append(self.now - arrival)
            elif not self.lo_q.is_empty():
                arrival, svc = await self.lo_q.get()
                await self.timeout(svc)
                self.sojourn_lo.append(self.now - arrival)
            else:
                await self.timeout(0.01)


class HiSource(Process):
    def init(self, rate: float, q: Queue):
        self.rate = rate
        self.q = q

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            svc = random.expovariate(SERVICE_RATE_HI)
            await self.q.put((self.now, svc))


class LoSource(Process):
    def init(self, q: Queue):
        self.q = q

    async def run(self):
        while True:
            await self.timeout(random.expovariate(ARRIVAL_RATE_LO))
            svc = random.expovariate(SERVICE_RATE_LO)
            await self.q.put((self.now, svc))


def simulate(
    arrival_rate_hi: float, use_aging: bool, seed: int = SEED
) -> tuple[list, list]:
    random.seed(seed)
    env = Environment()
    hi_q: Queue = Queue(env)
    lo_q: Queue = Queue(env)
    sojourn_hi: list[float] = []
    sojourn_lo: list[float] = []
    HiSource(env, arrival_rate_hi, hi_q)
    LoSource(env, lo_q)
    if use_aging:
        AgingServer(env, hi_q, lo_q, sojourn_hi, sojourn_lo)
    else:
        StaticPriorityServer(env, hi_q, lo_q, sojourn_hi, sojourn_lo)
    env.run(until=SIM_TIME)
    return sojourn_hi, sojourn_lo


def mean_or_none(lst: list) -> float | None:
    return statistics.mean(lst) if lst else None


def pct_or_none(lst: list, p: float) -> float | None:
    if not lst:
        return None
    return sorted(lst)[int(p * len(lst))]


# Part 1: sweep hi-priority utilization with static priority
sweep_rows = []
for rho_hi in [0.10, 0.20, 0.40, 0.60, 0.70, 0.80]:
    rate_hi = rho_hi * SERVICE_RATE_HI
    hi, lo = simulate(rate_hi, use_aging=False)
    rho_total = rho_hi + ARRIVAL_RATE_LO / SERVICE_RATE_LO
    sweep_rows.append(
        {
            "rho_hi": rho_hi,
            "rho_total": rho_total,
            "mean_W_hi": mean_or_none(hi),
            "mean_W_lo": mean_or_none(lo),
        }
    )

df_sweep = pl.DataFrame(sweep_rows)

# Part 2: static vs. aging at a fixed hi load where starvation is visible
FIXED_RHO_HI = 0.70
rate_hi = FIXED_RHO_HI * SERVICE_RATE_HI
rho_total = FIXED_RHO_HI + ARRIVAL_RATE_LO / SERVICE_RATE_LO

hi_static, lo_static = simulate(rate_hi, use_aging=False)
hi_aging, lo_aging = simulate(rate_hi, use_aging=True)

compare_rows = [
    {
        "policy": "static",
        "class": "hi",
        "n": len(hi_static),
        "mean_W": mean_or_none(hi_static),
        "p95": pct_or_none(hi_static, 0.95),
        "p99": pct_or_none(hi_static, 0.99),
    },
    {
        "policy": "static",
        "class": "lo",
        "n": len(lo_static),
        "mean_W": mean_or_none(lo_static),
        "p95": pct_or_none(lo_static, 0.95),
        "p99": pct_or_none(lo_static, 0.99),
    },
    {
        "policy": "aging",
        "class": "hi",
        "n": len(hi_aging),
        "mean_W": mean_or_none(hi_aging),
        "p95": pct_or_none(hi_aging, 0.95),
        "p99": pct_or_none(hi_aging, 0.99),
    },
    {
        "policy": "aging",
        "class": "lo",
        "n": len(lo_aging),
        "mean_W": mean_or_none(lo_aging),
        "p95": pct_or_none(lo_aging, 0.95),
        "p99": pct_or_none(lo_aging, 0.99),
    },
]
df_compare = pl.DataFrame(compare_rows)

print("Priority Starvation")
print(
    f"  lo-priority: arrival rate {ARRIVAL_RATE_LO}, "
    f"mean service {1 / SERVICE_RATE_LO:.1f}, rho_lo = {ARRIVAL_RATE_LO / SERVICE_RATE_LO:.2f}"
)
print(f"  Aging threshold: {AGING_THRESHOLD} time units")
print()
print("Part 1 — Static priority: effect of hi-priority load on lo-priority wait")
print(df_sweep)
print()
print(
    f"Part 2 — Static vs. aging at rho_hi={FIXED_RHO_HI:.2f}, rho_total={rho_total:.2f}"
)
print(df_compare)

df_plot = df_sweep.unpivot(
    on=["mean_W_hi", "mean_W_lo"],
    index=["rho_hi", "rho_total"],
    variable_name="job_class",
    value_name="mean_W",
)
sweep_chart = (
    alt.Chart(df_plot)
    .mark_line(point=True)
    .encode(
        x=alt.X("rho_hi:Q", title="Hi-priority utilization (ρ_hi)"),
        y=alt.Y("mean_W:Q", title="Mean sojourn time (W)"),
        color=alt.Color("job_class:N", title="Job class"),
        tooltip=["rho_hi:Q", "job_class:N", "mean_W:Q"],
    )
    .properties(title="Priority Starvation: Effect of Hi-Priority Load")
)
compare_chart = (
    alt.Chart(df_compare)
    .mark_bar()
    .encode(
        x=alt.X("class:N", title="Job class"),
        y=alt.Y("mean_W:Q", title="Mean sojourn time (W)"),
        color=alt.Color("policy:N", title="Policy"),
        xOffset="policy:N",
        tooltip=["policy:N", "class:N", "mean_W:Q", "p99:Q"],
    )
    .properties(title="Static Priority vs. Aging")
)
(sweep_chart | compare_chart).save(sys.argv[1])
