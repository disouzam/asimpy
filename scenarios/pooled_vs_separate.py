"""Pooled vs. separate queues: one shared line beats multiple dedicated lines."""

import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process, Resource

SIM_TIME = 100_000
ARRIVAL_RATE = 1.8  # total arrivals per time unit across both systems
SERVICE_RATE = 1.0  # per server
N_SERVERS = 2
SEED = 42

# Utilization per server: rho = arrival_rate / (n_servers * service_rate)
RHO = ARRIVAL_RATE / (N_SERVERS * SERVICE_RATE)


class Customer(Process):
    def init(self, server: Resource, sojourn_times: list):
        self.server = server
        self.sojourn_times = sojourn_times

    async def run(self):
        arrival = self.now
        async with self.server:
            await self.timeout(random.expovariate(SERVICE_RATE))
        self.sojourn_times.append(self.now - arrival)


class PooledArrivals(Process):
    """All customers join one shared queue feeding N_SERVERS servers."""

    def init(self, arrival_rate: float, server: Resource, sojourn_times: list):
        self.arrival_rate = arrival_rate
        self.server = server
        self.sojourn_times = sojourn_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.arrival_rate))
            Customer(self._env, self.server, self.sojourn_times)


class SeparateArrivals(Process):
    """Each customer randomly picks one of two dedicated servers and cannot switch."""

    def init(self, arrival_rate: float, servers: list[Resource], sojourn_times: list):
        self.arrival_rate = arrival_rate
        self.servers = servers
        self.sojourn_times = sojourn_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.arrival_rate))
            server = random.choice(self.servers)
            Customer(self._env, server, self.sojourn_times)


def run_pooled(arrival_rate: float = ARRIVAL_RATE, seed: int = SEED) -> float:
    random.seed(seed)
    sojourn_times: list[float] = []
    env = Environment()
    shared_server = Resource(env, capacity=N_SERVERS)
    PooledArrivals(env, arrival_rate, shared_server, sojourn_times)
    env.run(until=SIM_TIME)
    return statistics.mean(sojourn_times)


def run_separate(arrival_rate: float = ARRIVAL_RATE, seed: int = SEED) -> float:
    random.seed(seed)
    sojourn_times: list[float] = []
    env = Environment()
    servers = [Resource(env, capacity=1) for _ in range(N_SERVERS)]
    SeparateArrivals(env, arrival_rate, servers, sojourn_times)
    env.run(until=SIM_TIME)
    return statistics.mean(sojourn_times)


sweep_rows = []
for rho in [0.5, 0.6, 0.7, 0.8, 0.9]:
    rate = rho * N_SERVERS * SERVICE_RATE
    pw = run_pooled(arrival_rate=rate)
    sw = run_separate(arrival_rate=rate)
    sweep_rows.append({"rho": rho, "pooled_W": pw, "separate_W": sw, "ratio": sw / pw})

df_sweep = pl.DataFrame(sweep_rows)
print(f"Pooled vs. separate queues ({N_SERVERS} servers, service rate {SERVICE_RATE})")
print(df_sweep)

pooled_W = run_pooled()
separate_W = run_separate()
print(
    f"\nAt rho={RHO:.2f}: pooled_W={pooled_W:.3f}, separate_W={separate_W:.3f}, "
    f"separate is {separate_W / pooled_W:.2f}x slower"
)

df_plot = df_sweep.unpivot(
    on=["pooled_W", "separate_W"], index="rho", variable_name="system", value_name="W"
)
chart = (
    alt.Chart(df_plot)
    .mark_line(point=True)
    .encode(
        x=alt.X("rho:Q", title="Utilization per server (ρ)"),
        y=alt.Y("W:Q", title="Mean sojourn time (W)"),
        color=alt.Color("system:N", title="Queue type"),
        tooltip=["rho:Q", "system:N", "W:Q"],
    )
    .properties(title="Pooled vs. Separate Queues: Mean Sojourn Time")
)
chart.save(sys.argv[1])
