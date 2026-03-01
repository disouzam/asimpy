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
