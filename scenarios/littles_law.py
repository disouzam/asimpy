"""Little's Law holds universally: L = lambda * W across any queue configuration."""

import random
import statistics
import sys

import altair as alt
import polars as pl

from asimpy import Environment, Process, Resource

SIM_TIME = 200_000
SAMPLE_INTERVAL = 1.0  # how often the monitor samples queue length
SEED = 42


class Monitor(Process):
    """Periodically records number of customers currently in the system."""

    def init(self, in_system: list, samples: list):
        self.in_system = in_system
        self.samples = samples

    async def run(self):
        while True:
            self.samples.append(self.in_system[0])
            await self.timeout(SAMPLE_INTERVAL)


# ---------------------------------------------------------------------------
# Configuration 1: M/M/1 — Poisson arrivals, exponential service, 1 server
# ---------------------------------------------------------------------------


class MM1Customer(Process):
    def init(self, server: Resource, in_system: list, sojourn_times: list):
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times

    async def run(self):
        arrival = self.now
        self.in_system[0] += 1
        async with self.server:
            await self.timeout(random.expovariate(1.0))
        self.in_system[0] -= 1
        self.sojourn_times.append(self.now - arrival)


class MM1Arrivals(Process):
    def init(self, rate: float, server: Resource, in_system: list, sojourn_times: list):
        self.rate = rate
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            MM1Customer(self._env, self.server, self.in_system, self.sojourn_times)


# ---------------------------------------------------------------------------
# Configuration 2: M/D/1 — Poisson arrivals, deterministic service, 1 server
# ---------------------------------------------------------------------------


class MD1Customer(Process):
    def init(
        self,
        server: Resource,
        service_time: float,
        in_system: list,
        sojourn_times: list,
    ):
        self.server = server
        self.service_time = service_time
        self.in_system = in_system
        self.sojourn_times = sojourn_times

    async def run(self):
        arrival = self.now
        self.in_system[0] += 1
        async with self.server:
            await self.timeout(self.service_time)
        self.in_system[0] -= 1
        self.sojourn_times.append(self.now - arrival)


class MD1Arrivals(Process):
    def init(
        self,
        rate: float,
        service_time: float,
        server: Resource,
        in_system: list,
        sojourn_times: list,
    ):
        self.rate = rate
        self.service_time = service_time
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            MD1Customer(
                self._env,
                self.server,
                self.service_time,
                self.in_system,
                self.sojourn_times,
            )


# ---------------------------------------------------------------------------
# Configuration 3: M/M/3 — Poisson arrivals, exponential service, 3 servers
# ---------------------------------------------------------------------------


class MM3Customer(Process):
    def init(self, server: Resource, in_system: list, sojourn_times: list):
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times

    async def run(self):
        arrival = self.now
        self.in_system[0] += 1
        async with self.server:
            await self.timeout(random.expovariate(1.0))
        self.in_system[0] -= 1
        self.sojourn_times.append(self.now - arrival)


class MM3Arrivals(Process):
    def init(self, rate: float, server: Resource, in_system: list, sojourn_times: list):
        self.rate = rate
        self.server = server
        self.in_system = in_system
        self.sojourn_times = sojourn_times

    async def run(self):
        while True:
            await self.timeout(random.expovariate(self.rate))
            MM3Customer(self._env, self.server, self.in_system, self.sojourn_times)


# ---------------------------------------------------------------------------
# Run and verify
# ---------------------------------------------------------------------------


def verify(
    label: str,
    env: Environment,
    in_system: list,
    sojourn_times: list,
    samples: list,
    arrival_rate: float,
) -> dict:
    Monitor(env, in_system, samples)
    env.run(until=SIM_TIME)
    L_direct = statistics.mean(samples)
    W = statistics.mean(sojourn_times)
    n = len(sojourn_times)
    lam = n / SIM_TIME  # observed throughput
    L_little = lam * W  # Little's Law prediction
    error = 100.0 * (L_little - L_direct) / L_direct
    return {
        "label": label,
        "lambda_obs": lam,
        "mean_W": W,
        "L_direct": L_direct,
        "L_little": L_little,
        "error_pct": error,
    }


rows = []

random.seed(SEED)
lam1, mu1 = 0.7, 1.0
in_sys1: list[int] = [0]
soj1: list[float] = []
smp1: list[int] = []
env1 = Environment()
srv1 = Resource(env1, capacity=1)
MM1Arrivals(env1, lam1, srv1, in_sys1, soj1)
rows.append(verify("M/M/1 (rho=0.70, 1 server)", env1, in_sys1, soj1, smp1, lam1))

random.seed(SEED)
lam2, svc2 = 0.7, 1.0
in_sys2: list[int] = [0]
soj2: list[float] = []
smp2: list[int] = []
env2 = Environment()
srv2 = Resource(env2, capacity=1)
MD1Arrivals(env2, lam2, svc2, srv2, in_sys2, soj2)
rows.append(
    verify("M/D/1 (rho=0.70, deterministic service)", env2, in_sys2, soj2, smp2, lam2)
)

random.seed(SEED)
lam3 = 2.4
in_sys3: list[int] = [0]
soj3: list[float] = []
smp3: list[int] = []
env3 = Environment()
srv3 = Resource(env3, capacity=3)
MM3Arrivals(env3, lam3, srv3, in_sys3, soj3)
rows.append(
    verify("M/M/3 (rho=0.80 per server, 3 servers)", env3, in_sys3, soj3, smp3, lam3)
)

df = pl.DataFrame(rows)
print("Little's Law verification: L = lambda * W")
print(df)

points = (
    alt.Chart(df)
    .mark_point(size=100, filled=True)
    .encode(
        x=alt.X("L_direct:Q", title="L (direct sample)"),
        y=alt.Y("L_little:Q", title="L = λW (Little's Law)"),
        color=alt.Color("label:N", title="Configuration"),
        tooltip=["label:N", "L_direct:Q", "L_little:Q", "error_pct:Q"],
    )
)
max_val: float = max(df["L_direct"].to_list()) * 1.1
diagonal = (
    alt.Chart(pl.DataFrame({"x": [0.0, max_val], "y": [0.0, max_val]}))
    .mark_line(color="gray", strokeDash=[4, 4])
    .encode(x="x:Q", y="y:Q")
)
(diagonal + points).properties(title="Little's Law: Direct Sample vs. λW").save(
    sys.argv[1]
)
