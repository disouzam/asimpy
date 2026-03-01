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
