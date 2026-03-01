# Little's Law: The Universal Conservation Law of Queues

## The Law

Little's Law states that for any stable system in steady state:

$$L = \lambda W$$

where:

- $L$ is the long-run average number of customers in the system,
- $\lambda$ is the long-run average arrival rate (throughput),
- $W$ is the long-run average time a customer spends in the system.

## Why It Is Surprising

Little's Law holds **without any distributional assumptions**. It does not
matter whether arrivals are Poisson, deterministic, or correlated. It does not
matter whether service times are exponential, constant, or heavy-tailed. It
does not matter whether there is one server or one hundred, or what scheduling
discipline is used (FIFO, LIFO, random, priority). As long as the system is
stable and stationary, $L = \lambda W$ is exact.

This robustness is remarkable because almost every other performance formula
in queueing theory *does* depend on distributional assumptions.

## Three Configurations, One Law

The simulation verifies Little's Law independently for:

| Configuration | Arrivals     | Service       | Servers |
|--------------|-------------|---------------|---------|
| M/M/1        | Poisson($\lambda$) | Exp($\mu$)  | 1       |
| M/D/1        | Poisson($\lambda$) | Deterministic $1/\mu$ | 1 |
| M/M/3        | Poisson($\lambda$) | Exp($\mu$)  | 3       |

For each configuration, $L$ is estimated two independent ways:

1. **Direct sampling**: a monitor process samples the number of customers in
   the system every unit of simulated time; $L \approx \bar{n}_{\text{samples}}$.
2. **Little's Law**: throughput $\lambda$ (completed jobs / total time) and
   mean sojourn $W$ are measured; $L_{\text{Little}} = \lambda W$.

The two estimates agree to within simulation noise for all three very different
configurations.

## Proof Sketch

Consider a flow diagram where time runs horizontally and each customer traces
a horizontal line from arrival to departure. The area under all lines equals
both:

- $\sum_i W_i$ (sum of individual sojourn times), and
- $\int_0^T L(t)\,dt$ (integral of instantaneous queue length).

Dividing both sides by $T$ and taking $T \to \infty$:

$$\bar{L} = \lambda \bar{W}$$

The argument is purely combinatorial — no probability is needed.

## Practical Use

Because $L = \lambda W$ is universal, it can be used to measure hard-to-observe
quantities from easy-to-observe ones. For example, the mean number of requests
in a web server ($L$) and the observed request rate ($\lambda$) immediately
give the mean response time ($W = L/\lambda$) without needing to instrument
individual request latencies.
