"""Sojourn Time: how long a customer actually spends in the system.

The sojourn time W (arrival to departure) splits into two parts: Wq (time
spent waiting in the queue) and Ws (time spent in service).  For an M/M/1
queue, W = 1/(μ(1−ρ)).  Measuring all three confirms the decomposition and
demonstrates Little's Law: L = λW.
"""

import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process, Resource

SIM_TIME = 100_000
SERVICE_RATE = 1.0
SAMPLE_INTERVAL = 1.0
SEED = 42


class Customer(Process):
    def init(
        self,
        server: Resource,
        in_system: list[int],
        sojourn_times: list[float],
        wait_times: list[float],
    ):
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times
        self.wait_times = wait_times

    async def run(self):
        arrival = self.now
        self.in_system[0] += 1
        async with self.server:
            service_start = self.now
            await self.timeout(random.expovariate(SERVICE_RATE))
        self.in_system[0] -= 1
        self.sojourn_times.append(self.now - arrival)
        self.wait_times.append(service_start - arrival)


class Arrivals(Process):
    def init(
        self,
        rate: float,
        server: Resource,
        in_system: list[int],
        sojourn_times: list[float],
        wait_times: list[float],
    ):
        self.rate = rate
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times
        self.wait_times = wait_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            Customer(
                self._env,
                self.server,
                self.in_system,
                self.sojourn_times,
                self.wait_times,
            )


class Monitor(Process):
    def init(self, in_system: list[int], samples: list[int]):
        self.in_system = in_system
        self.samples = samples

    async def run(self):
        while True:
            self.samples.append(self.in_system[0])
            await self.timeout(SAMPLE_INTERVAL)


def simulate(rho: float, seed: int = SEED) -> dict:
    random.seed(seed)
    rate = rho * SERVICE_RATE
    env = Environment()
    server = Resource(env, capacity=1)
    in_system: list[int] = [0]
    sojourn_times: list[float] = []
    wait_times: list[float] = []
    samples: list[int] = []
    Arrivals(env, rate, server, in_system, sojourn_times, wait_times)
    Monitor(env, in_system, samples)
    env.run(until=SIM_TIME)
    mean_W = statistics.mean(sojourn_times)
    mean_Wq = statistics.mean(wait_times)
    mean_Ws = mean_W - mean_Wq
    mean_L = statistics.mean(samples)
    lam = len(sojourn_times) / SIM_TIME  # observed throughput
    return {
        "rho": rho,
        "mean_Wq": round(mean_Wq, 4),
        "mean_Ws": round(mean_Ws, 4),
        "mean_W": round(mean_W, 4),
        "theory_W": round(1.0 / (SERVICE_RATE * (1.0 - rho)), 4),
        "L_sampled": round(mean_L, 4),
        "L_little": round(lam * mean_W, 4),
    }


rows = [simulate(rho) for rho in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
df = pl.DataFrame(rows)

print("Sojourn Time: W = Wq + Ws  and  Little's Law L = λW")
print(f"  Service rate μ = {SERVICE_RATE}, simulation time = {SIM_TIME}")
print()
print(df)

# Stacked area chart: Wq + Ws = W across utilization levels
df_plot = df.select(["rho", "mean_Wq", "mean_Ws"]).unpivot(
    on=["mean_Wq", "mean_Ws"],
    index="rho",
    variable_name="component",
    value_name="time",
)
chart = (
    alt.Chart(df_plot)
    .mark_area()
    .encode(
        x=alt.X("rho:Q", title="Utilization (ρ)"),
        y=alt.Y("time:Q", title="Mean time", stack="zero"),
        color=alt.Color("component:N", title="Component"),
        tooltip=["rho:Q", "component:N", "time:Q"],
    )
    .properties(title="Sojourn Time Components: Wq (waiting) + Ws (service) = W")
)
chart.save(sys.argv[1])
