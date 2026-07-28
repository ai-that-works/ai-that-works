"""One budget definition must drive both the gate and the optimizer.

That claim is only true if the rendered weights actually differ between
modes. An earlier version returned `accuracy=1` for every budget, which
silently told the optimizer to ignore cost even in cost-down mode.
"""

from __future__ import annotations

from harness.budget import COST_DOWN, SURVIVE_THE_SWAP, Budget


class TestOptimizerWeights:
    def test_survival_mode_optimizes_purely_for_accuracy(self):
        """Headroom on cost and latency is not a demand to improve them."""
        assert SURVIVE_THE_SWAP.to_optimizer_weights() == "accuracy=1"

    def test_cost_down_mode_actually_asks_for_fewer_tokens(self):
        weights = COST_DOWN.to_optimizer_weights()
        assert "tokens=" in weights
        assert weights != "accuracy=1"

    def test_the_two_modes_render_differently(self):
        """If these ever match, the budget has stopped driving anything."""
        assert SURVIVE_THE_SWAP.to_optimizer_weights() != COST_DOWN.to_optimizer_weights()

    def test_latency_pressure_is_expressed(self):
        fast = Budget(max_cost_multiple=2.0, max_latency_multiple=0.8)
        weights = fast.to_optimizer_weights()
        assert "latency=" in weights and "tokens=" not in weights

    def test_pressure_on_both_splits_the_remainder(self):
        both = Budget(max_cost_multiple=0.5, max_latency_multiple=0.5)
        assert both.to_optimizer_weights() == "accuracy=0.6,tokens=0.2,latency=0.2"

    def test_weights_sum_to_one(self):
        for budget in (SURVIVE_THE_SWAP, COST_DOWN, Budget(max_latency_multiple=0.9)):
            total = sum(
                float(part.split("=")[1])
                for part in budget.to_optimizer_weights().split(",")
            )
            assert abs(total - 1.0) < 1e-9
