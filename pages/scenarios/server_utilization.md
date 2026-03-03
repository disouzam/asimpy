# Server Utilization: The Most Important Number in Queueing Theory

## Scenario

The previous scenario introduced arrivals.  This one introduces the other
half of a queue: the **server** — the cashier, the CPU core, the network
link — that does the work.

Service times are random too.  We model them as exponentially distributed
with rate $\mu$ (mu), meaning the server completes on average $\mu$ jobs per
unit time, with a mean service time of $1/\mu$.

With arrivals at rate $\lambda$ and service at rate $\mu$, the single most
important derived quantity is:

$$\rho = \frac{\lambda}{\mu}$$

$\rho$ (rho) is called the **utilization** or **traffic intensity**.

## The Surprising Finding

The fraction of time the server is busy converges to exactly $\rho$ in the
long run, regardless of the variability of service times.  The server is idle
exactly $1 - \rho$ of the time.

| Target $\rho$ | Busy fraction | Idle fraction |
|:---:|:---:|:---:|
| 0.50 | ≈ 0.50 | ≈ 0.50 |
| 0.80 | ≈ 0.80 | ≈ 0.20 |
| 0.95 | ≈ 0.95 | ≈ 0.05 |

This seems obvious — but the implication is striking: a server running at
$\rho = 0.95$ is idle only 5% of the time, yet customers still wait a
significant amount (as the next two scenarios will show).

### The Stability Condition

The system is **stable** only when $\rho < 1$.  When $\rho \geq 1$, arrivals
come at least as fast as the server can handle them.  The queue grows without
bound: every customer waits longer than the last.

When $\rho = 1$ (arrival rate exactly equals service rate), you might expect
the server to keep up.  It cannot.  Randomness in both arrivals and service
creates occasional bursts that the server falls behind on, and — with no slack
capacity to recover — the backlog accumulates forever.

### Measuring Utilization Directly

The simulation confirms $\rho = \lambda/\mu$ by measuring it directly.  Each
customer records how long it occupied the server.  The total service time
divided by the total simulation time gives the observed busy fraction:

$$\hat{\rho} = \frac{\text{total service time}}{T}$$

As the simulation runs longer, $\hat{\rho} \to \rho$.

## Why This Matters

Utilization is the first thing to calculate for any real system.  A web
server handling 800 requests per second with a mean response time of 1 ms
has utilization $\rho = 800 \times 0.001 = 0.8$, leaving 20% slack.  A
factory machine that processes 50 items per hour and receives 55 orders per
hour has $\rho = 55/50 = 1.1 > 1$ — it will fall further and further behind
over time.

## Implementation

The `Customer` process acquires the shared `Resource`, draws an exponential
service time, and accumulates it in a shared `total_service` list.
`Arrivals` generates customers with Poisson inter-arrival gaps.  After the
simulation, the busy fraction is `total_service[0] / SIM_TIME`.

The simulation sweeps $\rho$ from 0.1 to 0.95, confirming each time that
the observed busy fraction matches the target $\lambda/\mu$.

## Understanding the Math

**Why does the long-run busy fraction equal $\rho$?**  Here is an intuitive
argument using long-run averages.  Suppose the simulation runs for a long time
$T$ and $N$ customers are served.  By definition, $\lambda \approx N/T$
(arrivals per unit time), so $N \approx \lambda T$.  Each customer occupies
the server for an average of $1/\mu$ time units.  Total service time is
approximately $N/\mu = \lambda T / \mu = \rho T$.  Dividing by $T$:

$$\text{fraction busy} = \frac{\rho T}{T} = \rho$$

No calculus needed — just the definitions of $\lambda$, $\mu$, and $\rho$.

**What does $\rho < 1$ mean geometrically?**  Think of a bank account.  Each
arriving job makes a "deposit" of work (service time) into the server's
backlog.  Each unit of clock time makes a "withdrawal" of $\mu$ units of
work (service capacity).  When $\lambda/\mu < 1$, withdrawals outpace
deposits in the long run and the balance (queue length) stays bounded.  When
$\lambda/\mu \geq 1$, deposits outpace withdrawals and the balance grows
without limit.

**The exponential service time and its coefficient of variation.**  Recall
from the arrival process scenario that the exponential distribution has mean
equal to standard deviation.  Its **coefficient of variation** — standard
deviation divided by mean — is therefore $\text{CV} = 1$.  A deterministic
server (every job takes exactly $1/\mu$) has CV = 0.  A highly variable server
(some jobs very short, some very long) has CV $> 1$.  The CV of service times
matters enormously for queue length, as later scenarios will show.

**Why randomness prevents $\rho = 1$ from being stable.**  Suppose $\rho = 1$.
Gaps between arrivals and service times are both exponential with the same
mean.  The queue length after each service completion performs a random walk:
it goes up by 1 when a new arrival joins while the server is busy, and down
by 1 when service finishes.  A symmetric random walk (equal probability of
going up or down) is known from probability theory to be null-recurrent: it
returns to zero, but the expected return time is infinite.  This means the
expected queue length is infinite even at exact balance.

**Practical rule of thumb.**  Engineers routinely target $\rho \leq 0.7$–$0.8$
for interactive systems, because queue length and wait time grow sharply as
$\rho$ approaches 1 — a fact the next two scenarios quantify precisely.
