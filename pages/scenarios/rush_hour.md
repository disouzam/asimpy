# Rush Hour Displacement: If Everyone Avoids the Rush, It Shifts

## Scenario

$N$ commuters all want to leave for work at the same preferred time. The road
has a fixed capacity: up to $C$ commuters per time slot travel quickly, but
when more than $C$ try to leave in the same slot, everyone in that slot
experiences extra delay proportional to the overload.

Each day, commuters observe yesterday's travel times and shift their departure
by one slot toward a less congested option with some probability.

## The Surprising Finding

The rush hour **never disappears**. Instead it:

1. Flattens slightly (spreading across more slots), but
2. Shifts its peak position over successive days, and
3. Reaches a new quasi-equilibrium that may be *no less congested* than the
   original, just at a different time.

The intuition is that any slot that becomes less congested immediately attracts
new commuters from adjacent overloaded slots, refilling it. Individual
optimization is self-defeating in aggregate.

## The Vickrey Bottleneck Model

The classic model (Vickrey 1969) treats the road as a bottleneck with flow
rate $s$ vehicles per unit time. At equilibrium, every commuter faces the
same **generalized cost**:

$$c = \alpha \cdot d + \beta \cdot \max(0,\, t^* - t_{\text{arr}}) + \gamma \cdot \max(0,\, t_{\text{arr}} - t^*)$$

where $d$ is queuing delay, $t^*$ is the desired arrival time, and
$\beta, \gamma$ are schedule-delay costs for early and late arrival
respectively. Vickrey showed that at Nash equilibrium a departure queue
forms with length that rises and then falls as commuters spread across time
to equalize cost — but total system delay is unchanged.

This model underlies modern road-pricing schemes: a time-varying toll that
exactly offsets the schedule-delay cost eliminates queuing entirely while
preserving the total commuting burden (the toll revenue replaces the wasted
queuing time).

## Emergent Behaviour

The simulation shows **emergent dynamics**:

- The arrival distribution begins concentrated at the preferred slot.
- Commuters shift away from congested slots, spreading the peak.
- The spreading creates new local peaks at adjacent slots, which then
  attract their own shifters.
- Over many days the distribution oscillates or drifts without converging
  to zero congestion.

This is a concrete example of the **tragedy of the commons**: a shared resource
(road capacity) that individuals overuse because the full cost of their choice
is not borne privately. Each commuter's rational decision to leave at a
popular time imposes a negative externality on all others at that time.

## Implementation

Rather than one continuous DES run, the simulation iterates over days.
Each day's commute is computed analytically: the travel time for slot $s$
is $\delta_{\text{base}}$ when occupancy $\leq C$, and increases linearly
with overflow otherwise. Commuters update their departure slot between days
using a simple best-response rule with noise (they shift to a better
neighbour with probability $p$). The resulting day-by-day trajectory
of the departure distribution and mean delay is printed as a compact table.
