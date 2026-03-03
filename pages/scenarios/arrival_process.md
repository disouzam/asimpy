# Arrival Process: The Building Block of Every Queue

## Scenario

Before studying queues, we need to understand how customers arrive.
This scenario asks a simple question: if customers arrive at random — no one
coordinates with anyone else, and past events do not influence future ones —
what mathematical pattern do those arrivals follow?

The answer is the **Poisson process**, named after the French mathematician
Siméon Denis Poisson.  It is parameterized by a single number $\lambda$
(lambda), called the **arrival rate** or **intensity**, measured in arrivals
per unit time.

## The Surprising Finding

The Poisson process has two equivalent signatures:

1. **Gaps are exponentially distributed**: the time between consecutive
   arrivals follows an exponential distribution with mean $1/\lambda$.
2. **Counts are Poisson-distributed**: the number of arrivals in any window
   of width $t$ follows a Poisson distribution with mean $\lambda t$.

These are not two separate assumptions — they are the same fact viewed from
two angles.  If one holds, the other must hold automatically.

### The Exponential Distribution of Gaps

If $X$ is the time until the next arrival, then:

$$P(X > t) = e^{-\lambda t}$$

The mean gap is $E[X] = 1/\lambda$ and the standard deviation is
$\text{SD}[X] = 1/\lambda$.  Mean equals standard deviation — this equality
is the defining signature of the exponential distribution.

A stranger consequence is the **memoryless property**.  If you have already
waited $s$ units for the next arrival, the remaining wait is still
exponentially distributed with the same mean $1/\lambda$:

$$P(X > s + t \mid X > s) = P(X > t)$$

The next arrival is never "overdue."  Knowing you have already waited a long
time gives no information about when the next arrival will come.

### The Poisson Distribution of Counts

If $K$ is the number of arrivals in a window of width $t$, then:

$$P(K = k) = \frac{(\lambda t)^k \, e^{-\lambda t}}{k!}$$

The mean and variance of $K$ are both equal to $\lambda t$.  The fact that
mean equals variance is the hallmark of the Poisson distribution, and a
direct consequence of the memoryless property.

## When Is the Poisson Model Appropriate?

The Poisson process is a good model when:

- Arrivals are **independent** — one customer's arrival does not influence
  another's.
- The rate $\lambda$ is roughly **constant** over the time window of interest.
- **Simultaneous** arrivals are essentially impossible (probability zero).

It fits customer arrivals at a supermarket during a quiet hour, web requests
to a server, or emergency calls to a dispatch centre.  It is a poor fit when
customers arrive in groups (e.g., fans leaving a stadium), or on a fixed
schedule (e.g., hourly buses).

## Implementation

An `ArrivalSource` process generates arrivals by drawing each inter-arrival
gap from `random.expovariate(rate)` — Python's built-in generator for
exponentially distributed random numbers — then advancing the simulation
clock by that gap.

After the run, window counts are tallied by dividing the time axis into
non-overlapping intervals of width `WINDOW` and counting how many recorded
arrivals land in each.  The observed distribution is compared against the
theoretical Poisson probabilities computed directly from the formula.

## Understanding the Math

**Where does $e^{-\lambda t}$ come from?**  Imagine dividing the interval
$[0, t]$ into $n$ tiny slices of width $\Delta = t/n$.  In each slice,
the probability of an arrival is approximately $\lambda \Delta = \lambda t/n$
(arrival rate times slice width), and slices are independent.  The probability
of *zero* arrivals in all $n$ slices is approximately
$(1 - \lambda t / n)^n$.  From introductory calculus you know that
$\lim_{n \to \infty}(1 - x/n)^n = e^{-x}$, so the probability of no arrival
in $[0,t]$ is $e^{-\lambda t}$.  This is exactly $P(X > t)$.

**Where does the factorial $k!$ come from?**  $P(K = k)$ is the probability
of exactly $k$ arrivals and zero arrivals in the remaining time.  The $k!$
in the denominator corrects for the fact that the $k$ arrivals are
indistinguishable — we do not care about the order in which they occur,
only that there are exactly $k$ of them.  This is the same factorial that
appears in the binomial coefficient $\binom{n}{k} = n!/(k!(n-k)!)$ from
your statistics class.

**Why does mean equal standard deviation for the exponential?**  The mean
of $X \sim \text{Exp}(\lambda)$ requires integration by parts (a first-year
calculus technique):

$$E[X] = \int_0^\infty t \cdot \lambda e^{-\lambda t}\, dt = \frac{1}{\lambda}$$

The second moment $E[X^2] = 2/\lambda^2$, so
$\text{Var}(X) = E[X^2] - (E[X])^2 = 2/\lambda^2 - 1/\lambda^2 = 1/\lambda^2$,
giving $\text{SD}(X) = 1/\lambda = E[X]$.  Equal mean and standard deviation
means the distribution is highly variable: roughly one-third of gaps are longer
than the mean.

**Why does mean equal variance for the Poisson?**  The count $K$ in a window
is the sum of $n$ independent Bernoulli trials (one per tiny slice), each with
success probability $p = \lambda t / n$.  A Bernoulli trial has mean $p$ and
variance $p(1-p)$.  Summing $n$ independent trials gives mean $np = \lambda t$
and variance $np(1-p) \approx np = \lambda t$ as $n \to \infty$ and
$p \to 0$.  So mean and variance both equal $\lambda t$.

**What the simulation confirms.**  Running the simulation with $\lambda = 2$
and windows of width 1 should give an observed count distribution very close
to Poisson(2): mostly 2 arrivals per window, rarely 0 or 5+.  The measured
$1/\lambda$ from the gap data should also match 0.5, and the standard deviation
of gaps should equal the mean — the two sides of the exponential's
equal-mean-and-SD property.
