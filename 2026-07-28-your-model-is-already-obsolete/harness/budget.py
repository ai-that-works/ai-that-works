"""The regression budget: how much worse than today you'll tolerate.

Everything is expressed RELATIVE TO THE INCUMBENT. That's the whole idea.
Absolute thresholds ("must hit 95%") are numbers you invented, they go
stale every model generation, and they can block a swap that is strictly
better than what you're running today.

    You don't need the new model to be good.
    You need it to be no worse.

Flip the multiples and the same harness becomes a cost-down tool: hunt for
the cheapest model that still clears the accuracy bar.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    """Tolerances, as multiples of the incumbent's measured performance."""

    #: Accuracy may drop by at most this much, in absolute percentage
    #: points. 0.0 means "no regression at all".
    max_accuracy_drop: float = 0.0

    #: Cost per call may be at most this multiple of the incumbent's.
    max_cost_multiple: float = 1.2

    #: p95 latency may be at most this multiple of the incumbent's.
    max_latency_multiple: float = 1.5

    def to_optimizer_weights(self) -> str:
        """Render as `baml-cli optimize --weight` argument.

        The optimizer accepts the same three objectives the gate judges on,
        so one budget definition drives both. Whatever you refuse to
        regress on is what the optimizer is told to protect.
        """
        # Weight follows PRESSURE, not tolerance. A multiple at or below
        # 1.0 means you are actively demanding an improvement on that
        # dimension, so the optimizer should spend effort there. A
        # multiple above 1.0 is mere headroom and earns no weight —
        # otherwise every budget renders as accuracy=1 and the optimizer
        # never hears about cost at all.
        pressured = []
        if self.max_cost_multiple <= 1.0:
            pressured.append("tokens")
        if self.max_latency_multiple <= 1.0:
            pressured.append("latency")

        if not pressured:
            return "accuracy=1"

        accuracy = 0.6
        share = (1.0 - accuracy) / len(pressured)
        parts = [f"accuracy={accuracy:g}"]
        parts += [f"{name}={share:g}" for name in pressured]
        return ",".join(parts)


#: Surviving a deprecation: hold quality, tolerate a little more cost.
SURVIVE_THE_SWAP = Budget()

#: Deliberately going cheaper: quality must hold, cost must actually fall.
COST_DOWN = Budget(
    max_accuracy_drop=0.0,
    max_cost_multiple=0.5,
    max_latency_multiple=2.0,
)
