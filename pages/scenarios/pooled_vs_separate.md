# Pooled vs. Separate Queues: Why Banks Switched to Single Lines

## Scenario

A facility has two identical servers (bank tellers, airport check-in desks,
toll booths). Customers arrive as a Poisson process and each needs one server
for an exponentially distributed service time.

Two queue disciplines are compared:

- **Separate queues**: each server has its own dedicated line; customers
  randomly pick a line on arrival and cannot switch.
- **Pooled queue**: a single shared line feeds whichever server becomes free
  first (the "supermarket" or "serpentine" model).

## The Surprising Finding

Pooling the queues is *always* better, even though both systems have identical
total arrival rate, identical per-server service rate, and identical
utilization $\rho$. The pooled system consistently produces shorter mean wait
times, often by a factor of two or more at moderate utilization.

The intuition is **wasted idle time**. In separate queues, one server may be
idle while customers wait in the other line. Pooling eliminates this mismatch:
a free server always serves the next waiting customer.

## Analysis

For a pooled M/M/2 queue the mean number in the system is:

$$L_{\text{pooled}} = \frac{2\rho^3}{1 - \rho^2} \cdot \frac{1}{2} + 2\rho$$

where $\rho = \lambda / (2\mu)$. The Erlang-C formula gives the probability
that an arriving customer must wait:

$$C(2, \lambda/\mu) = \frac{(\lambda/\mu)^2 / (2!(1-\rho))}{1 + \lambda/\mu + (\lambda/\mu)^2/(2!(1-\rho))}$$

For two separate M/M/1 queues each receiving half the traffic at utilization
$\rho$, the mean sojourn time per customer is:

$$W_{\text{separate}} = \frac{1}{\mu(1-\rho)}$$

The pooled system has strictly lower mean sojourn time for all $0 < \rho < 1$.

## Why Separate Queues Persist

Despite being provably worse, separate queues feel "fair" because customers
can see their progress. Single lines eliminate the anxiety of watching the
other queue move faster — but historically customers resisted them until
airlines and banks demonstrated the improvement empirically in the 1960s–70s.

## Implementation

Two simulations run with identical seeds:

1. **Pooled**: `Resource(capacity=2)` with one arrival stream — the resource
   grants access to whichever capacity slot is free.
2. **Separate**: two `Resource(capacity=1)` instances; arrivals call
   `random.choice` to pick a server and cannot switch even if it is slower.

Mean sojourn time is collected with Little's Law $W = L/\lambda$.

## Understanding the Math

**What variance measures.** The variance $\sigma^2$ of a random variable tells you how spread out its values are. If a random variable has low variance, almost every observation is close to the mean. High variance means the values are scattered widely. In queueing, high variance in arrival times means customers sometimes arrive in bunches and sometimes leave long gaps — and that unpredictability is costly.

**The idle-time problem.** With two separate queues, the randomness of arrivals can leave one server standing idle while customers queue in the other lane. That idle time is wasted capacity: the idle server could have helped, but customers who already chose the busy lane cannot switch. Pooling a single line into both servers eliminates this mismatch — a free server immediately picks up the next person in line, regardless of which "lane" that person would have joined.

**A simple example.** Suppose each server handles exactly one job every 2 minutes, and jobs arrive at exactly one every 2 minutes — so $\rho = 1/2$. Now suppose two jobs happen to arrive at the same instant. With separate queues, one server gets both jobs and takes 4 minutes total; the other server sits idle for 2 minutes. With a pooled queue, one job goes to each server and both finish in 2 minutes. No wasted capacity, shorter total wait.

**Why pooling always wins.** Two separate M/M/1 queues each running at utilization $\rho$ have mean sojourn time $W_{\text{sep}} = 1/(\mu(1-\rho))$. A pooled M/M/2 queue with the same total arrival rate has strictly lower mean sojourn time for every value of $0 < \rho < 1$. The proof uses the Erlang-C formula, but the intuition is simpler: pooling converts two independent random processes into one, and the combined queue can exploit any idle capacity instantly. At $\rho = 0.8$, separate queues give roughly twice the mean wait of a pooled queue.

**Connection to variance reduction.** Think of the service delivered in a time window by two separate servers as two independent random variables $X_1$ and $X_2$. Their average $(X_1 + X_2)/2$ has variance $\sigma^2/2$ — half the variance of either component alone. Pooling achieves something similar: by combining demand into one stream served by both servers, the system smooths out random fluctuations. The pooled queue is, in effect, averaging over both servers' idle periods instead of locking each idle period to a single lane.

**Rule of thumb.** At $\rho = 0.8$, separate queues produce roughly double the mean wait of a pooled queue. This factor grows as $\rho$ increases, because the $(1-\rho)$ term in the denominator amplifies any wasted capacity. The lesson: whenever you can route demand flexibly to a shared resource, do it.
