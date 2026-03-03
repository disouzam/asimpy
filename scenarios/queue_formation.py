"""Queue Formation: randomness creates waiting even when the server has spare capacity.

At any utilization ρ < 1 the queue is stable — it does not grow forever —
but random fluctuations cause customers to wait even though the server handles
more than enough work on average.  The mean number of customers in the system
is L = ρ/(1−ρ), which grows without bound as ρ approaches 1.
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
    def init(self, server: Resource, in_system: list[int]):
        self.server = server
        self.in_system = in_system

    async def run(self):
        self.in_system[0] += 1
        async with self.server:
            await self.timeout(random.expovariate(SERVICE_RATE))
        self.in_system[0] -= 1


class Arrivals(Process):
    def init(self, rate: float, server: Resource, in_system: list[int]):
        self.rate = rate
        self.server = server
        self.in_system = in_system

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            Customer(self._env, self.server, self.in_system)


class Monitor(Process):
    """Samples total customers in system at regular intervals."""

    def init(self, in_system: list[int], samples: list[int]):
        self.in_system = in_system
        self.samples = samples

    async def run(self):
        while True:
            self.samples.append(self.in_system[0])
            await self.timeout(SAMPLE_INTERVAL)


def simulate(rho: float, seed: int = SEED) -> dict:
    random.seed(seed)
    arrival_rate = rho * SERVICE_RATE
    env = Environment()
    server = Resource(env, capacity=1)
    in_system: list[int] = [0]
    samples: list[int] = []
    Arrivals(env, arrival_rate, server, in_system)
    Monitor(env, in_system, samples)
    env.run(until=SIM_TIME)
    sim_L = statistics.mean(samples)
    theory_L = rho / (1.0 - rho)
    return {
        "rho": rho,
        "sim_L": round(sim_L, 4),
        "theory_L": round(theory_L, 4),
        "error_pct": round(100.0 * (sim_L - theory_L) / theory_L, 2),
    }


rows = [simulate(rho) for rho in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
df = pl.DataFrame(rows)

print("Queue Formation: Mean Queue Length L = ρ/(1−ρ)")
print(f"  Service rate μ = {SERVICE_RATE}, simulation time = {SIM_TIME}")
print()
print(df)

df_plot = df.unpivot(
    on=["sim_L", "theory_L"],
    index="rho",
    variable_name="source",
    value_name="L",
)
chart = (
    alt.Chart(df_plot)
    .mark_line(point=True)
    .encode(
        x=alt.X("rho:Q", title="Utilization (ρ)"),
        y=alt.Y("L:Q", title="Mean customers in system (L)"),
        color=alt.Color("source:N", title="Source"),
        tooltip=["rho:Q", "source:N", "L:Q"],
    )
    .properties(title="Queue Formation: Simulated vs. Theoretical L = ρ/(1−ρ)")
)
chart.save(sys.argv[1])
