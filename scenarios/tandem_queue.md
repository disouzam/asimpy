# Tandem Queue Blocking: Variability Travels Downstream

## Scenario

Two processing stages are arranged in series: Stage 1 feeds work into a
bounded buffer, which feeds Stage 2. Both stages have the **same mean
service rate** $\mu$, and the arrival rate $\lambda < \mu$ so neither stage
is overloaded on average.

Stage 1 has **high variance** (hyperexponential service); Stage 2 has
**zero variance** (deterministic service).

## The Surprising Finding

Even though both stages have identical mean throughput and the system is
underloaded, Stage 2 sits idle for a substantial fraction of time when the
buffer between them is small. The idle fraction only vanishes as the buffer
size $K \to \infty$.

High service-time variance at Stage 1 produces bursts of output — many jobs
finish close together — followed by droughts. With a small buffer, the
burst overflows (blocking Stage 1) and the drought starves Stage 2. Both
effects reduce system throughput below the theoretical maximum.

## Analysis

For a two-stage tandem queue with a finite buffer of capacity $K$, the
blocking probability at Stage 1 and the starvation probability at Stage 2
depend on the full service-time distributions, not just their means. The
Kingman approximation gives the mean wait in a single G/G/1 queue as:

$$W_q \approx \frac{\rho}{1-\rho} \cdot \frac{c_a^2 + c_s^2}{2} \cdot \frac{1}{\mu}$$

where $c_a^2$ and $c_s^2$ are the squared coefficients of variation of
inter-arrival and service times respectively. For a hyperexponential service
distribution with $c_s^2 \gg 1$, waiting times are far higher than the
M/M/1 formula predicts.

In a tandem network, this extra variability propagates: the departure process
of Stage 1 (which is the arrival process for Stage 2) has higher variance
than Poisson when Stage 1 has high service variance. This is **Departure
Process Variability Propagation** and is a key driver of manufacturing and
supply-chain bullwhip effects.

## Buffer as a Variability Absorber

The buffer acts as a shock absorber. Each unit of additional buffer capacity
$K$ reduces the starvation probability at Stage 2 by absorbing burst output
from Stage 1. The marginal benefit decreases as $K$ grows — a classic
diminishing-returns relationship. Practitioners use this to size work-in-progress
inventory (WIP) buffers in manufacturing cells.

## Implementation

- A `Source` process generates jobs with exponential inter-arrival times
  into an unlimited input queue.
- `Stage1` pulls from the input queue, applies a hyperexponential service
  delay, and pushes to a bounded `Queue(max_capacity=K)`. If the buffer is
  full, Stage 1 blocks (back-pressure).
- `Stage2` pulls from the bounded buffer, applies deterministic service, and
  records completion times.
- Stage 2 idle time is measured as the wait inside `queue.get()` (time spent
  waiting for work to appear).

The simulation sweeps $K$ from 1 to 21 and reports Stage 2 idle fraction.
