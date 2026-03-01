# The Convoy Effect: One Slow Job Ruins Everyone's Day

## Scenario

A single server processes jobs that arrive randomly (Poisson process). Most
jobs are quick (exponential service with small mean), but a rare few are very
slow (exponential service with large mean). This **hyperexponential** service
distribution has high variance.

Two scheduling disciplines are compared:

- **FIFO**: jobs are served in the order they arrive.
- **SJF** (Shortest Job First): the server always picks the shortest queued
  job next.

## The Surprising Finding

SJF dramatically outperforms FIFO — not just for the small jobs that directly
benefit from skipping ahead, but also for mean sojourn time across *all* jobs.
The improvement is most visible at the tail (95th and 99th percentiles) because
FIFO creates **convoy effects**: one long job blocks many short jobs behind it,
inflating everyone's wait.

### Why FIFO Hurts with High Variance

In FIFO, the server's current job is chosen at arrival time, not at decision
time. When a slow job begins service, every subsequent arrival must join the
queue and wait. The expected excess work in service (the remaining time of the
current job, seen by an arriving customer) under FIFO is:

$$W_{\text{FIFO}} = \frac{\lambda \overline{s^2}}{2(1-\rho)} + \frac{1}{\mu}$$

where $\overline{s^2}$ is the second moment of service time. High variance
inflates $\overline{s^2}$ without changing $\rho$, directly worsening wait time.

### SJF Minimises Mean Sojourn Time

For a single server with non-preemptive SJF and any service-time distribution,
the mean sojourn time equals the M/G/1 Pollaczek–Khinchine formula evaluated
at the *minimum* possible work:

$$W_{\text{SJF}} = \frac{1}{\mu} + \frac{\lambda \overline{s^2}}{2(1-\rho)}$$

SJF achieves this minimum because short jobs that would otherwise be blocked
by a long job are promoted ahead, reducing the total waiting work in the system.

## Practical Relevance

Operating system CPU schedulers use time-quanta and priority aging to
approximate SJF without knowing job sizes in advance. Database query planners
estimate query cost and reorder execution to minimize blocking. Web servers use
connection queuing strategies to avoid head-of-line blocking.

The phenomenon reappears as **head-of-line blocking** in HTTP/1.1 (one slow
response stalls a connection), motivating HTTP/2 multiplexing and HTTP/3's
QUIC stream independence.

## Implementation

Jobs are placed in a `Queue(priority=True)` for SJF (tupled as
`(service_time, job_id)` so shorter jobs sort earlier) or a plain `Queue()`
for FIFO (tupled as `(job_id, service_time)` to preserve arrival order).
The same hyperexponential service-time generator (90% short, 10% long) is
used in both runs.
