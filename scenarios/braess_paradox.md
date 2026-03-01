# Braess's Paradox: Adding a Road Makes Traffic Worse

## Scenario

A city has two routes from source $S$ to destination $T$:

- **Top route** $S \to A \to T$: link $SA$ is congestion-dependent; link $AT$
  has a fixed travel time.
- **Bottom route** $S \to B \to T$: link $SB$ has a fixed travel time; link
  $BT$ is congestion-dependent.

The network is symmetric. A city planner proposes adding a new shortcut link
$A \to B$ with near-zero travel time, creating a third route
$S \to A \to B \to T$.

## The Surprising Finding

Adding the shortcut makes **everyone's travel time longer** at the
selfish-routing Nash equilibrium.

### Without the shortcut

Both routes are symmetric. In equilibrium, traffic splits evenly. If $N/2$
drivers use each route and the congested links have delay $\alpha \cdot n$
(where $n$ is the number of cars):

$$t_{\text{top}} = \frac{N}{2}\alpha + c = t_{\text{bottom}}$$

### With the shortcut $A \to B$

Each driver reasons: *"Link $AB$ is free; I can use $SA$, slip across to $B$,
then take $BT$ instead of the slow constant link $AT$."* All $N$ drivers
make this choice. The Nash equilibrium has everyone on $S \to A \to B \to T$:

$$t_{\text{shortcut}} = N\alpha + \varepsilon + N\alpha = 2N\alpha + \varepsilon$$

Since $2N\alpha > \frac{N}{2}\alpha + c$ for typical parameters, travel times
*increase* after the road is added. This is the paradox: individually rational
decisions produce a collectively worse outcome.

### The Price of Anarchy

The ratio of Nash equilibrium cost to the socially optimal cost is called the
**price of anarchy**. For Braess networks it can exceed 1 with congestion
functions $t(x) = ax + b$:

$$\text{PoA} = \frac{t_{\text{Nash}}}{t_{\text{optimal}}} > 1$$

## Real-World Evidence

The paradox is not merely theoretical. Seoul (Cheonggyecheon Expressway,
2003), Stuttgart, and New York have all observed traffic *improvements* after
closing roads. Conversely, new roads in highly congested networks have
sometimes worsened average travel times.

## Implementation

The simulation maintains a shared `LinkCounts` object tracking how many cars
are currently on each link. Each `Car` process:

1. Observes current link counts and computes expected travel time for each
   available route.
2. Greedily picks the route with minimum expected time.
3. Traverses each link in sequence, incrementing the count on entry and
   decrementing on exit; the delay is fixed at the count observed on entry.

Two runs are compared — one with only the top and bottom routes, one with the
$AB$ shortcut added.
