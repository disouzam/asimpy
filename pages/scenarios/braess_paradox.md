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

## Understanding the Math

**Nash equilibrium.** A Nash equilibrium is a situation where every player has chosen a strategy and no single player can improve their own outcome by switching to a different strategy — assuming everyone else stays put. It is named after mathematician John Nash. Think of it as a stable fixed point: if you woke up one morning in a Nash equilibrium, you would have no reason to change what you are doing. Crucially, a Nash equilibrium need not be the best possible outcome for everyone collectively.

**The paradox, step by step.** Label the number of cars $N$ and suppose the congested links have delay $\alpha \cdot n$ where $n$ is the number of cars currently using that link. Without the shortcut, traffic splits evenly: $N/2$ cars use each route. Each driver's travel time is $(N/2)\alpha + c$, where $c$ is the fixed delay on the non-congested link. Neither route is faster than the other, so no driver wants to switch — that is Nash equilibrium.

Now add the shortcut $A \to B$ with near-zero travel time $\varepsilon$. A single driver considering a switch reasons: "Link $AB$ is essentially free. If I take $SA$, cross to $B$, and take $BT$, I avoid the fixed cost $c$." If that driver is the only one to switch, it looks cheaper. But every driver makes the same calculation simultaneously. At the new equilibrium, all $N$ drivers pile onto $SA$ and $BT$:

$$t_{\text{shortcut}} = N\alpha + \varepsilon + N\alpha = 2N\alpha + \varepsilon$$

Since $2N\alpha > (N/2)\alpha + c$ for typical parameters, everyone is worse off than before the shortcut was built.

**Price of anarchy.** The ratio of Nash equilibrium cost to the socially optimal cost is called the price of anarchy. Here the social optimum would split traffic evenly at cost $(N/2)\alpha + c$, but selfish routing delivers $2N\alpha + \varepsilon$. The price of anarchy exceeds 1, meaning individual rationality destroys collective welfare.

**A two-player analogy.** The Prisoner's Dilemma is the classic example of this tension. Two suspects each choose independently to cooperate or defect. Defecting is a dominant strategy — it is better for you regardless of what the other person does. Yet if both defect, both get a worse outcome than if both had cooperated. Braess's paradox is the same logic scaled to $N$ drivers.

**The logit model.** The simulation uses a probabilistic choice rule: the probability a driver picks route $r$ is proportional to $\exp(-\beta \cdot t_r)$, where $t_r$ is the expected travel time on route $r$ and $\beta$ is a sensitivity parameter. This is the softmax function from statistics. When $\beta$ is large, drivers strongly prefer the fastest route and the outcome approaches the pure Nash equilibrium. When $\beta$ is small, drivers choose nearly randomly and the paradox weakens. The parameter $\beta$ captures how responsive real drivers are to time differences.
