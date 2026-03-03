# Queue Formation: Randomness Creates Waiting Even with Spare Capacity

## Scenario

We now combine arrivals (Poisson at rate $\lambda$) with a server (exponential
service at rate $\mu$) into a complete queue.  The system is stable because
$\rho = \lambda/\mu < 1$.  The server handles more work than arrives, on
average.

How long is the queue?

## The Surprising Finding

Even when the server has plenty of spare capacity, customers wait.  The mean
number of customers in the system (waiting *and* being served) is:

$$L = \frac{\rho}{1 - \rho}$$

| $\rho$ | $L$ |
|:---:|:---:|
| 0.1 | 0.11 |
| 0.5 | 1.00 |
| 0.8 | 4.00 |
| 0.9 | 9.00 |

At $\rho = 0.5$ — with half the server's capacity sitting idle — there is
on average one customer in the system at any moment.  That customer either
had to wait for a previous customer, or is currently being served.  The queue
is *never* consistently empty, even at moderate load.

The formula also explains why the M/M/1 queue is so sensitive to utilization:
$L$ blows up as $\rho \to 1$.  The denominator $(1 - \rho)$ is the "spare
capacity."  As spare capacity vanishes, queue length diverges.

### Why Queues Form at All

With deterministic arrivals and service (every customer arrives exactly
$1/\lambda$ apart and takes exactly $1/\mu$), a server with $\rho < 1$
would never form a queue: each customer departs before the next arrives.

Randomness changes this.  Sometimes three customers arrive close together
before the server finishes even one.  The server falls briefly behind.  It
recovers — but in the meantime, customers wait.  These temporary pileups are
unavoidable whenever inter-arrival or service times have any variance.

### The Geometric Distribution of Queue Length

The probability that exactly $n$ customers are in an M/M/1 system at
steady state is:

$$P(N = n) = (1 - \rho)\,\rho^n \qquad n = 0, 1, 2, \ldots$$

This is a **geometric distribution** with success probability $1 - \rho$.
The formula says the server is idle (n = 0) with probability $1 - \rho$ —
consistent with the utilization result from the previous scenario — and each
additional customer in the system is $\rho$ times less likely than the
previous count.

## Connection to Later Scenarios

This formula $L = \rho/(1-\rho)$ is the foundation of the
[M/M/1 nonlinearity scenario](mm1_nonlinearity.md), which shows the
practical consequences of the $(1-\rho)$ denominator.  Every queue-length
formula in queueing theory has a similar structure: a traffic factor
$\rho$ divided by a spare-capacity factor $(1 - \rho)$, possibly multiplied
by a variability correction.

## Implementation

A `Customer` process increments a shared `in_system` counter on arrival and
decrements it on departure.  A `Monitor` process samples `in_system[0]` every
`SAMPLE_INTERVAL` time units.  After the simulation, the mean of the samples
estimates $L$.  The theoretical value $\rho/(1-\rho)$ is computed and compared.

The simulation sweeps $\rho$ from 0.1 to 0.9, confirming the formula at each
load level.

## Understanding the Math

**Deriving $L = \rho/(1-\rho)$ from the geometric distribution.**  Given
$P(N = n) = (1 - \rho)\rho^n$, the mean is:

$$L = E[N] = \sum_{n=0}^{\infty} n \cdot (1-\rho)\rho^n = (1-\rho) \sum_{n=0}^{\infty} n\rho^n$$

You may have seen the geometric series $\sum_{n=0}^{\infty} \rho^n = 1/(1-\rho)$
in your calculus course.  Differentiating both sides with respect to $\rho$:

$$\sum_{n=0}^{\infty} n\rho^{n-1} = \frac{1}{(1-\rho)^2}$$

Multiply both sides by $\rho$:

$$\sum_{n=0}^{\infty} n\rho^n = \frac{\rho}{(1-\rho)^2}$$

Substituting back:

$$L = (1-\rho) \cdot \frac{\rho}{(1-\rho)^2} = \frac{\rho}{1-\rho}$$

**Why is the queue length geometric?**  The M/M/1 queue can be analyzed as
a random walk on the non-negative integers.  When the server is busy, the
queue grows by 1 with each arrival (rate $\lambda$) and shrinks by 1 with
each service completion (rate $\mu$).  The ratio $\lambda/\mu = \rho$ is the
probability that the queue grows rather than shrinks at the next event.
Under steady state, the probability of being at level $n$ is proportional to
$\rho^n$ — because reaching level $n$ requires $n$ consecutive "up" steps.
Normalizing so the probabilities sum to 1 gives $(1-\rho)\rho^n$.

**Checking the formula at the boundaries.**  When $\rho \to 0$: almost no
arrivals, so $L \to 0$ — the server is nearly always idle.  When $\rho \to 1$:
spare capacity $(1-\rho) \to 0$, so $L \to \infty$ — the queue grows without
bound.  Both limits match physical intuition.  The formula is exact (not an
approximation) for M/M/1 queues in steady state.

**What the simulation measures.**  The `Monitor` process records how many
customers are in the system every unit of simulated time.  The time-average
of this sequence estimates $L$.  By the law of large numbers, this converges
to the true steady-state mean as the simulation time grows.
