"""Server Utilization: the fraction of time a server is busy equals ρ = λ/μ.

ρ (rho) is the single most important number in queueing theory.  It is the
ratio of arrival rate to service rate.  When ρ < 1 the system is stable;
when ρ ≥ 1 the queue grows without bound.  This scenario measures the actual
busy fraction of the server and confirms it equals ρ.
"""

import random
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process, Resource

SIM_TIME = 100_000
SERVICE_RATE = 1.0  # μ: average service completions per unit time
SEED = 42


class Customer(Process):
    """Requests the server, receives exponential service, records service time."""

    def init(self, server: Resource, total_service: list[float]):
        self.server = server
        self.total_service = total_service

    async def run(self):
        async with self.server:
            svc = random.expovariate(SERVICE_RATE)
            await self.timeout(svc)
            self.total_service[0] += svc


class Arrivals(Process):
    def init(self, rate: float, server: Resource, total_service: list[float]):
        self.rate = rate
        self.server = server
        self.total_service = total_service

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            Customer(self._env, self.server, self.total_service)


def simulate(rho: float, seed: int = SEED) -> dict:
    random.seed(seed)
    arrival_rate = rho * SERVICE_RATE
    env = Environment()
    server = Resource(env, capacity=1)
    total_service: list[float] = [0.0]
    Arrivals(env, arrival_rate, server, total_service)
    env.run(until=SIM_TIME)
    busy_frac = total_service[0] / SIM_TIME
    return {
        "rho_target": rho,
        "rho_observed": round(busy_frac, 4),
        "idle_frac": round(1.0 - busy_frac, 4),
    }


rows = [simulate(rho) for rho in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]]
df = pl.DataFrame(rows)

print("Server Utilization: ρ = λ/μ")
print(f"  Service rate μ = {SERVICE_RATE}, simulation time = {SIM_TIME}")
print()
print(df)

df_plot = df.unpivot(
    on=["rho_observed", "idle_frac"],
    index="rho_target",
    variable_name="metric",
    value_name="fraction",
)
chart = (
    alt.Chart(df_plot)
    .mark_line(point=True)
    .encode(
        x=alt.X("rho_target:Q", title="Target utilization (ρ = λ/μ)"),
        y=alt.Y("fraction:Q", title="Fraction of time"),
        color=alt.Color("metric:N", title="Metric"),
        tooltip=["rho_target:Q", "metric:N", "fraction:Q"],
    )
    .properties(title="Server Utilization: Busy and Idle Fractions vs. ρ")
)
chart.save(sys.argv[1])
