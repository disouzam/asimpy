# M/M/1 Queue Nonlinearity: The 90% Utilization Trap

## Scenario

A single server (cashier, CPU, network link) handles jobs that arrive randomly
and take a random amount of time to process. Both inter-arrival times and
service times follow exponential distributions — the simplest possible model,
known as the **M/M/1 queue**.

## The Surprising Finding

Managers often treat utilization linearly: "90% busy is only a little worse
than 80% busy." The M/M/1 formula shows this intuition is badly wrong.

The mean number of jobs in the system (waiting *and* being served) is:

$$L = \frac{\rho}{1 - \rho}$$

where $\rho = \lambda / \mu$ is the utilization ratio (arrival rate divided by
service rate). The mean time a job spends in the system follows from
Little's Law $L = \lambda W$:

$$W = \frac{1}{\mu - \lambda} = \frac{1}{\mu(1 - \rho)}$$

The denominator $(1 - \rho)$ causes both $L$ and $W$ to blow up as $\rho \to 1$.

| $\rho$ | $L = \rho/(1-\rho)$ | Marginal $\Delta L$ per 0.1 step |
|-------:|--------------------:|--------------------------------:|
|  0.50  |               1.00  |                            —    |
|  0.60  |               1.50  |                          +0.50  |
|  0.70  |               2.33  |                          +0.83  |
|  0.80  |               4.00  |                          +1.67  |
|  0.90  |               9.00  |                          +5.00  |

Each equal step in $\rho$ produces a *larger* jump in queue length than the
previous step. Going from 80% to 90% utilization adds more queue length than
going from 0% to 80% combined.

## Why This Happens

The queue is stabilized by the gaps in service capacity. When $\rho = 0.9$,
only 10% of capacity is "slack." Any random burst of arrivals takes far longer
to drain than when $\rho = 0.5$ and 50% of capacity is slack. The system
spends most of its time recovering from bursts rather than idling.

## Implementation

The simulation uses a single `Resource(capacity=1)` as the server. A
generator process creates customers with inter-arrival gaps drawn from
$\text{Exp}(\lambda)$. Each customer records its arrival time, waits to
`acquire` the server, receives $\text{Exp}(\mu)$ service, and logs its
total sojourn time. Mean queue length $L$ is computed via Little's Law
$L = \lambda \bar{W}$ from the observed mean sojourn time $\bar{W}$.

## Key Takeaway

For any system approximated by an M/M/1 queue, **never target utilization
above 80–85%** if low latency matters. The last few percent of throughput
come at an enormous cost in queue length and wait time.

## Understanding the Math

Let's build up the M/M/1 result from scratch so you can see exactly where the blow-up comes from.

**The two rates.** Call $\lambda$ (the Greek letter lambda) the arrival rate — for example, 3 customers per minute. Call $\mu$ (the Greek letter mu) the service rate — for example, 4 customers per minute. Both rates are averages; the actual gaps between events are random. The utilization $\rho = \lambda / \mu$ is simply the fraction of time the server is busy. With $\lambda = 3$ and $\mu = 4$, we get $\rho = 0.75$, meaning the server is occupied 75% of the time on average.

**Stability.** If $\rho \geq 1$, customers arrive at least as fast as the server can handle them, so the queue grows without limit. We need $\rho < 1$ for the system to be stable — for the queue to have a finite average length.

**The geometric distribution.** When arrivals and service times are both exponential (that's the "M/M" in M/M/1), the probability that exactly $k$ jobs are in the system at any moment is:

$$P(k) = (1 - \rho)\,\rho^k, \quad k = 0, 1, 2, \ldots$$

This is a geometric distribution. It says the server is idle with probability $1 - \rho$, has exactly 1 job with probability $(1-\rho)\rho$, has 2 jobs with probability $(1-\rho)\rho^2$, and so on. You can verify these sum to 1 using the standard geometric series $\sum_{k=0}^{\infty} \rho^k = 1/(1-\rho)$.

**Deriving $L$.** The mean number of jobs in the system is:

$$L = \sum_{k=0}^{\infty} k \cdot P(k) = (1-\rho) \sum_{k=0}^{\infty} k\,\rho^k$$

From first-year calculus, you can show that $\sum_{k=0}^{\infty} k\,x^k = x/(1-x)^2$ for $|x| < 1$ (differentiate both sides of the geometric series with respect to $x$). Substituting $x = \rho$:

$$L = (1-\rho) \cdot \frac{\rho}{(1-\rho)^2} = \frac{\rho}{1-\rho}$$

**Why the denominator causes blow-up.** As $\rho \to 1$, the denominator $(1-\rho)$ approaches zero, so $L \to \infty$. Think of $(1-\rho)$ as the server's spare capacity. When spare capacity is small, any random burst of arrivals takes a very long time to drain. The server is so busy that it can never fully "catch up" before the next burst arrives.

**A concrete analogy.** Imagine a single supermarket checkout lane. Suppose the cashier scans items at exactly the same average rate that customers arrive. On average everything is balanced — but averages hide randomness. Sometimes three customers arrive in quick succession. The cashier works through them eventually, but by then two more have joined. The queue keeps growing because there is no cushion of spare capacity to absorb unlucky stretches. Push $\rho$ to 0.9 and that cushion shrinks to just 10%; the queue becomes nine times as long as at $\rho = 0.5$. The math shows this isn't a gradual worsening — it's an explosion driven by the $(1-\rho)$ term in the denominator.
