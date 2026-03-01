# Late (Zipper) Merge: Courtesy Reduces Throughput

## Scenario

A two-lane road narrows to one lane at a construction zone. Drivers face a
choice:

- **Early (courtesy) merge**: upon seeing the "Lane Ends Ahead" sign, drivers
  immediately move from the closing lane into the open lane.
- **Late (zipper) merge**: drivers use both lanes all the way to the merge
  point, then alternate — one car from each lane in turn, like a zipper.

## The Surprising Finding

Late merging produces **higher throughput and shorter queues** than early
merging, even though it feels less polite. Early merging creates a single
long queue that wastes the closing lane's capacity. Late merging fully
utilises both lanes up to the bottleneck, then processes cars at the same
rate with a zipper pattern.

This result is not merely theoretical: the Minnesota Department of
Transportation, the German ADAC, and the UK Highway Code all recommend late
merging in slow-moving traffic precisely because it is provably more efficient.

## Why Early Merging Hurts

With early merging:

- All $N$ cars queue in one lane of capacity $K$.
- When the single queue is full ($K$ cars), arriving cars are turned away
  (blocking), reducing throughput.
- The merge point processes at rate $\mu$ regardless, but there are fewer
  cars available to process (the second lane is empty and wasted).

With late merging:

- Cars distribute across two lanes, each of capacity $K$ (total $2K$).
- The merge point receives supply from both lanes, reducing starvation.
- Blocking occurs only when *both* lanes are simultaneously full, a rarer event.

The key metric is the **blocking probability**: the fraction of arriving cars
turned away because the pre-merge buffer is full. Let $\rho = \lambda/\mu$ be
the utilisation of the merge bottleneck. For a finite-buffer M/M/1/K queue
the blocking probability is:

$$P_{\text{block}} = \frac{(1-\rho)\rho^K}{1 - \rho^{K+1}}$$

Early merge has buffer $K$; late merge effectively has buffer $2K$ (spread
across two lanes). Since $P_{\text{block}}$ decreases exponentially in $K$,
doubling the available buffer dramatically reduces blocking.

## Throughput vs. Mean Sojourn

The primary benefit of late merging is **higher throughput**: more cars
complete the merge per unit time. Mean sojourn time for individual cars may
actually be slightly longer under late merge, because the larger total buffer
admits more cars into the system, increasing average queue occupancy. By
Little's Law $L = \lambda W$, if $\lambda$ grows faster than $L$ falls,
$W$ rises. This is not a disadvantage: it means more drivers successfully
pass through rather than being turned away.

## Implementation

- **Early merge**: one `Queue(max_capacity=LANE_CAPACITY)` feeds a single
  `MergeServer`. Arrivals that find the lane full are counted as blocked and
  turned away.
- **Late merge**: two `Queue(max_capacity=LANE_CAPACITY)` instances feed a
  zipper `MergeServer` that alternates between lanes. Arrivals pick the
  shorter lane; a car is blocked only if its chosen lane is full.

Both systems have the same total arrival rate $\lambda$ and merge service
rate $\mu$.
