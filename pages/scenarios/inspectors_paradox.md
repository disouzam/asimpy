# The Inspector's Paradox: Why the Bus Is Always Late

## Scenario

Buses arrive at a stop with some average headway (gap between buses) of
$\mu$ minutes. A passenger arrives at a uniformly random time and waits
for the next bus. How long do they wait?

The naive answer is $\mu / 2$: on average you land in the middle of a gap.
The correct answer is almost always *longer* — sometimes much longer.

## The Surprising Finding

The expected wait is not $\mu/2$ but:

$$E[\text{wait}] = \frac{\mu}{2} + \frac{\sigma^2}{2\mu}$$

where $\sigma^2 = \text{Var}[\text{headway}]$. The second term is always
non-negative, so higher variance always means longer expected waits, even
when the mean headway is unchanged.

### Three Bus Schedules with Mean Headway $\mu = 10$

| Schedule    | $\sigma^2$ | Predicted wait | Naive wait |
|-------------|-----------|----------------|-----------|
| Regular     | 0         | 5.0            | 5.0       |
| Exponential | 100       | 10.0           | 5.0       |
| Clustered   | 64        | 8.2            | 5.0       |

For exponentially distributed headways, $\sigma^2 = \mu^2$, so:

$$E[\text{wait}] = \frac{\mu}{2} + \frac{\mu^2}{2\mu} = \mu$$

A passenger waits on average for an *entire* mean headway — twice the naive
expectation.

## Why This Happens: Length-Biased Sampling

A passenger arriving at a random time is more likely to land inside a *long*
gap than a short one, because long gaps occupy more time on the clock. This
is called **length-biased sampling**. The interval containing your arrival is
not a random headway — it is drawn from the length-biased distribution with
density:

$$f^*(h) = \frac{h \cdot f(h)}{\mu}$$

The mean of this biased distribution is $\mu + \sigma^2/\mu$, and you
arrive uniformly within it, giving expected wait $(\mu + \sigma^2/\mu)/2$.

The same phenomenon explains why:

- The average class size experienced by a student exceeds the average class
  size reported by the university (large classes have more students to report
  them).
- The average file size observed during a random disk read is larger than the
  mean file size (larger files occupy more sectors).

## Implementation

A `BusService` process generates buses under three headway distributions
(regular, exponential, clustered bimodal) and records their arrival times.
After the simulation, passenger wait times are estimated by sampling
$N = 20{,}000$ uniformly random arrival times and finding the next bus for
each, without needing explicit `Passenger` processes.
