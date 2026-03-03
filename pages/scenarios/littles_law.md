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

## Understanding the Math

**The area argument, made concrete.** Draw a horizontal time axis from $t = 0$ to $t = T$. Each customer gets a horizontal bar starting at their arrival time and ending at their departure time. The length of their bar is exactly their sojourn time $W_i$ — the total time they spend in the system. At any moment $t$, the number of bars that cross that vertical slice is exactly $L(t)$, the instantaneous number of customers in the system.

Now compute the total area under all the bars in two different ways. First, add up the lengths of all the bars: total area $= \sum_i W_i$. Second, integrate the height of the stack over time: total area $= \int_0^T L(t)\,dt$. These are the same area, so $\sum_i W_i = \int_0^T L(t)\,dt$.

Divide both sides by $T$. The right side becomes the time-average $\bar{L}$. The left side becomes $(n/T) \cdot \bar{W}$, where $n$ is the total number of customers and $\bar{W}$ is their mean sojourn time. As $T \to \infty$, $n/T \to \lambda$ (the long-run arrival rate). That gives $\bar{L} = \lambda \bar{W}$, which is Little's Law.

**No distribution required.** The argument above uses only geometry — counting rectangles. There is no probability distribution, no exponential assumption, no Poisson process. The shape of each bar (i.e., how long each customer takes) can be anything. This is why the law applies to M/M/1, M/D/1, M/M/3, and every other configuration equally.

**Using it in practice.** Suppose you run a web service. Your monitoring dashboard shows $\lambda = 500$ requests per second and your server logs show a mean response time of $W = 20$ milliseconds. Little's Law immediately tells you that the mean number of active requests in the system is $L = \lambda W = 500 \times 0.02 = 10$ requests. Alternatively, if you observe $L$ and $\lambda$ but not individual response times, you get $W = L/\lambda$ without any per-request timing instrumentation.

**Units check.** $\lambda$ has units of customers per unit time; $W$ has units of time; so $L = \lambda W$ is dimensionless — a pure count of customers. Always verify units when applying Little's Law to a new problem: if your units do not cancel correctly, you have applied the law incorrectly.

**Stability condition.** Little's Law requires the system to reach steady state: over the long run, arrivals and departures must balance. If $\lambda > \mu$ (the arrival rate exceeds the service rate), the queue grows without bound. $L = \infty$ and $W = \infty$; the law still holds, but it tells you the system is broken, not that it is well-behaved.
