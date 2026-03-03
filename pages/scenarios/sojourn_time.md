# Sojourn Time: How Long Does a Customer Actually Spend in the System?

## Scenario

The previous scenario measured $L$, the mean number of customers in the
system at any moment.  This scenario measures $W$, the mean time a single
customer spends from arrival to departure — the **sojourn time** (also called
**residence time** or **response time**).

$W$ has two components:

- $W_q$: time spent **waiting in the queue** (server is busy).
- $W_s$: time spent **in service** (server is working on this customer).

$$W = W_q + W_s$$

## The Surprising Finding

For an M/M/1 queue, the mean sojourn time is:

$$W = \frac{1}{\mu(1 - \rho)}$$

This blows up as $\rho \to 1$, just like $L$.  But the split between
waiting and service shifts dramatically as load increases.

| $\rho$ | $W_q$ (wait) | $W_s$ (service) | $W$ (total) |
|:---:|:---:|:---:|:---:|
| 0.1 | 0.11 | 1.00 | 1.11 |
| 0.5 | 1.00 | 1.00 | 2.00 |
| 0.9 | 9.00 | 1.00 | 10.00 |

Mean service time $W_s = 1/\mu = 1.0$ is **constant** — the server always
takes the same average time to serve one customer.  All the extra delay at
high load is pure waiting: $W_q = \rho/(\mu(1-\rho))$ grows without bound
while $W_s$ stays fixed.  At $\rho = 0.9$, 90% of a customer's time is spent
waiting for the server to become free.

## Little's Law: $L = \lambda W$

The simulation also verifies **Little's Law**, one of the most powerful
results in queueing theory:

$$L = \lambda W$$

Plugging in $W = 1/(\mu(1-\rho))$ and $\lambda = \rho\mu$:

$$L = \rho\mu \cdot \frac{1}{\mu(1-\rho)} = \frac{\rho}{1-\rho}$$

This is exactly the formula from the previous scenario.  Little's Law
connects $L$ (what you observe at a snapshot of the system) to $W$ (what
any individual customer experiences) via $\lambda$ (the throughput).
It holds for *any* stable queue, regardless of distributions.

## Connection to Later Scenarios

$W = 1/(\mu(1-\rho))$ is the M/M/1 baseline.  Every other scenario in this
collection compares against this baseline or modifies it:

- The [M/M/1 nonlinearity scenario](mm1_nonlinearity.md) studies the
  $(1-\rho)$ denominator in detail.
- The [Little's Law scenario](littles_law.md) verifies $L = \lambda W$ for
  M/M/1, M/D/1, and M/M/3 queues.
- The [pooled queues scenario](pooled_vs_separate.md) compares $W$ for
  pooled vs. separate servers.
- The [convoy effect scenario](convoy_effect.md) shows how high service-time
  variance inflates $W_q$ far beyond the M/M/1 prediction.

## Implementation

`Customer` records its arrival time, then captures the exact moment it enters
service (`service_start = self.now` inside the `async with self.server:` block,
which only executes once the resource is acquired).  The wait time is
`service_start − arrival` and the sojourn time is `departure − arrival`.

A `Monitor` samples the `in_system` counter periodically to estimate $L$
independently.  The final dataframe reports $W_q$, $W_s$, $W$, the theoretical
$W$, $L$ from sampling, and $L$ from Little's Law, allowing all three to be
cross-checked.

## Understanding the Math

**Deriving $W$ from $L$ using Little's Law.**  We already know
$L = \rho/(1-\rho)$.  Little's Law says $L = \lambda W$, so:

$$W = \frac{L}{\lambda} = \frac{\rho/(1-\rho)}{\lambda}$$

Substituting $\lambda = \rho\mu$:

$$W = \frac{\rho/(1-\rho)}{\rho\mu} = \frac{1}{\mu(1-\rho)}$$

This is elegant: the formula for $W$ follows directly from the formula for
$L$ and Little's Law — no separate derivation needed.

**Why $W_s = 1/\mu$ regardless of $\rho$.**  Service time is drawn from
an exponential distribution with rate $\mu$, so its mean is $1/\mu$.  This
is a property of the distribution, not of the queue.  No matter how busy the
server is, once it starts serving you it takes on average $1/\mu$ time.

**Deriving $W_q$.**  Since $W = W_q + W_s$ and $W_s = 1/\mu$:

$$W_q = W - W_s = \frac{1}{\mu(1-\rho)} - \frac{1}{\mu}
      = \frac{1}{\mu}\left(\frac{1}{1-\rho} - 1\right)
      = \frac{1}{\mu} \cdot \frac{\rho}{1-\rho}
      = \frac{\rho}{\mu(1-\rho)}$$

Note that $W_q = \rho \cdot W$: at high load, almost all of $W$ is waiting.

**Units check.**  $\lambda$ has units of [customers/time]; $W$ has units of
[time]; so $L = \lambda W$ has units of [customers/time $\times$ time]
$=$ [customers].  This is dimensionless — a count of people — as it should be.
Checking units this way is a quick sanity test whenever you apply Little's Law
to a real problem.

**The area proof of Little's Law.**  Draw a time axis.  Each customer is a
horizontal bar from arrival to departure, at height 1.  The stack of bars at
any moment $t$ has height $L(t)$ (the current number in system).  The total
shaded area is both $\sum_i W_i$ (sum of bar widths) and $\int_0^T L(t)\,dt$.
Dividing by $T$: $\bar{L} = (N/T) \cdot \overline{W} = \lambda W$.  No
probability is required — just geometry — which is why the law holds for
any distribution.
