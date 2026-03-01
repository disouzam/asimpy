# Priority Starvation: When High-Priority Traffic Crowds Out Low-Priority Jobs

## Scenario

A single server processes two job classes:

- **High-priority** jobs (class H): arrive frequently, served quickly.
- **Low-priority** jobs (class L): arrive rarely, take longer to serve.

The server always picks the highest-priority job available. Total server
utilization $\rho = \rho_H + \rho_L < 1$, so the server has spare capacity
on average. Yet low-priority jobs can wait far longer than the utilization
level suggests they should.

## The Surprising Finding

### Static Priority: Starvation at Moderate Load

With a static priority queue, high-priority jobs *never* yield to low-priority
ones. Even when $\rho_H < 1$, high-priority bursts can lock out low-priority
jobs for extended periods. The mean wait for low-priority jobs under a static
non-preemptive priority queue is:

$$W_L = \frac{\overline{s}_L}{1-\rho_H} \cdot \frac{1}{1-\rho_H-\rho_L}$$

This diverges as $\rho_H \to 1$ independently of $\rho_L$. As $\rho_H$
approaches 100%, low-priority jobs wait arbitrarily long — even if only a few
low-priority jobs ever arrive.

### Aging: Solving Starvation Creates Oscillation

The standard remedy for starvation is **priority aging**: a waiting job's
priority improves over time until it eventually beats even high-priority
arrivals. This guarantees finite wait for all jobs.

However, aging introduces a new pathology. When aged low-priority jobs finally
burst through, they occupy the server and leave a backlog of high-priority jobs
waiting. The high-priority queue then drains, and the cycle repeats — producing
**oscillating bursts** rather than smooth, uniform service.

## Mean Wait Formula for Two-Priority Queues

Let $\lambda_i$, $\mu_i$, and $\rho_i = \lambda_i / \mu_i$ be the arrival
rate, service rate, and utilization of class $i \in \{H, L\}$. For a
non-preemptive priority queue:

$$W_H = \frac{R_0}{1 - \rho_H}$$

$$W_L = \frac{R_0}{(1 - \rho_H)(1 - \rho_H - \rho_L)}$$

where $R_0 = \tfrac{1}{2}(\lambda_H \overline{s_H^2} + \lambda_L \overline{s_L^2})$
is the mean residual work seen by an arriving customer. The ratio
$W_L / W_H = 1/(1 - \rho_H)$ grows without bound as $\rho_H \to 1$.

## Practical Implications

Priority queues appear throughout computing:

- **OS scheduling**: interactive processes (high priority) vs. batch jobs
  (low priority). Linux uses dynamic priority aging (nice values + sleep
  bonuses) to avoid starvation.
- **Network QoS**: real-time traffic (VoIP, video) vs. bulk data. Traffic
  shaping with Deficit Round Robin (DRR) or Weighted Fair Queuing (WFQ)
  guarantees bandwidth shares without starvation.
- **Database query planning**: short OLTP queries vs. long OLAP queries.
  Resource groups and query timeouts implement a form of aging.

## Implementation

Two runs are compared:

1. **Static priority**: H jobs are inserted as `(0, ...)` and L jobs as
   `(1, ...)` into a `Queue(priority=True)`. The server always picks the
   smallest key first, so H jobs are always served before L jobs.
2. **Aging**: an `Ager` process wakes up every `AGING_INTERVAL` time units,
   inspects waiting L jobs, and promotes sufficiently old ones by reducing
   their priority key until it falls below the H threshold and they move into
   the server's feed queue.
