"""M/M/1 queue: mean queue length grows nonlinearly with utilization."""

import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process, Resource

SIM_TIME = 100_000
SERVICE_RATE = 1.0
SEED = 42


class Customer(Process):
    def init(self, server: Resource, service_rate: float, sojourn_times: list):
        self.server = server
        self.service_rate = service_rate
        self.sojourn_times = sojourn_times

    async def run(self):
        arrival = self.now
        async with self.server:
            await self.timeout(random.expovariate(self.service_rate))
        self.sojourn_times.append(self.now - arrival)


class ArrivalStream(Process):
    def init(
        self,
        arrival_rate: float,
        service_rate: float,
        server: Resource,
        sojourn_times: list,
    ):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.server = server
        self.sojourn_times = sojourn_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.arrival_rate))
            Customer(self._env, self.server, self.service_rate, self.sojourn_times)


def simulate(
    rho: float, sim_time: float = SIM_TIME, seed: int = SEED
) -> tuple[float, float]:
    """Return (simulated L, theoretical L) for M/M/1 at utilization rho."""
    random.seed(seed)
    arrival_rate = rho * SERVICE_RATE
    sojourn_times: list[float] = []
    env = Environment()
    server = Resource(env, capacity=1)
    ArrivalStream(env, arrival_rate, SERVICE_RATE, server, sojourn_times)
    env.run(until=sim_time)
    mean_W = statistics.mean(sojourn_times) if sojourn_times else 0.0
    sim_L = arrival_rate * mean_W  # Little's Law: L = lambda * W
    theory_L = rho / (1.0 - rho)  # M/M/1 exact result
    return sim_L, theory_L


rhos = [0.1, 0.2, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95]

sweep_rows = []
for rho in rhos:
    sim_L, theory_L = simulate(rho)
    pct = 100.0 * (sim_L - theory_L) / theory_L
    sweep_rows.append(
        {"rho": rho, "theory_L": theory_L, "sim_L": sim_L, "pct_error": pct}
    )

df_sweep = pl.DataFrame(sweep_rows)
print("M/M/1 nonlinearity: simulated vs. theoretical queue length")
print(df_sweep)

marginal_rows = []
prev_L, prev_rho = None, None
for rho in [0.5, 0.6, 0.7, 0.8, 0.9]:
    theory_L = rho / (1.0 - rho)
    if prev_L is not None:
        marginal_rows.append(
            {"rho_from": prev_rho, "rho_to": rho, "delta_L": theory_L - prev_L}
        )
    prev_L, prev_rho = theory_L, rho

df_marginal = pl.DataFrame(marginal_rows)
print("\nMarginal increase in L per 0.1 step in rho (theory):")
print(df_marginal)

df_plot = df_sweep.unpivot(
    on=["theory_L", "sim_L"], index="rho", variable_name="source", value_name="L"
)
chart = (
    alt.Chart(df_plot)
    .mark_line(point=True)
    .encode(
        x=alt.X("rho:Q", title="Utilization (ρ)"),
        y=alt.Y("L:Q", title="Mean queue length (L)"),
        color=alt.Color("source:N", title="Source"),
        tooltip=["rho:Q", "source:N", "L:Q"],
    )
    .properties(title="M/M/1 Queue Length vs. Utilization")
)
chart.save(sys.argv[1])
