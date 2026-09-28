# Cross-Family Memory Comparison: The Condition Law

Four families, one protocol (P46 recovery/weak/variant arcs), two memory
types (structural vs episodic). The law:

**Structural memory beats episodic memory on recovery and drift IFF the
sufficient statistic produces a compact discrete partition (C1 AND C2
of the P50 two-condition law).**

| Family | C1 extraction | C2 novelty hull | STR | EPI | Winner |
|---|---|---|---|---|---|
| t-combinatorial | YES | YES | 83.7% | 82.5% (ALL) | STR |
| envelope ladder | YES | PARTIAL | 15.2%* | 84.8% (ALL) | EPI |
| Markov authors | PARTIAL | NO | 87.6% | n/a | both fail novelty |
| oscillators | YES | NO | 89.8% | 90.9% (ALL) | tie |

*envelope STR-centroid fails because centroid smoothing destroys the
local boundary in a continuous overlapping ladder; with normalized
cosine centroids it recovers to 52.5% but still underperforms EPI-ALL.

**The two-condition law**: recognition accuracy requires C1 (extraction
quality -- does the representation expose the class signal?); novelty
detection requires C1 AND C2 (does the representation place the new
class outside the known hull?). Neither condition alone suffices; both
are family-dependent.

**The discovery threshold** (P40-b/P42/P43): the sufficient statistic
must be discoverable at the available sample size. The MI/MDL-gain rank
correlation rises from 0.565 (m=10) to 0.890 (m=40) -- below m*, the
compressor finds features that compress but do not inform.

**The phase boundary** (P47): on matched geometry, both memory arms
rise monotonically with Delta/sigma, transitioning between ratio 1 and
2. The memory-type choice is secondary to the gap-to-noise ratio.
