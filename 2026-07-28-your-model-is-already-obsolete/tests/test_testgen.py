"""The corpus -> BAML test block bridge.

`baml-cli optimize` reads its corpus from BAML `test` blocks and nothing
else. If this renders wrong, the optimizer does not fail — it completes,
scores a flat pass rate, and improves nothing, which costs real money and
looks like a weak model.
"""

from __future__ import annotations

from harness.corpus import CORPUS, Case, Gold
from harness.testgen import render, render_case


class TestNeverEmitsNull:
    """`null` is not a BAML Jinja literal. `== null` is ALWAYS FALSE.

    This exact mistake made every candidate score 33.3% and sent the
    optimizer chasing an unsatisfiable assertion for a full run, without
    ever reporting that the metric itself was broken.
    """

    def test_no_assertion_ever_compares_against_null(self):
        # Scoped to assertion lines: the header comment mentions `null` on
        # purpose, to explain why it must never appear in an assertion.
        offenders = [
            line
            for line in render().splitlines()
            if "@@assert" in line and "null" in line
        ]
        assert not offenders, offenders

    def test_omitted_tax_asserts_against_none(self):
        case = Case(
            name="x",
            document="doc",
            gold=Gold(category="Meals", total=1.0, n_items=1, tax_is_none=True),
        )
        assert "this.tax == none" in render_case(case)

    def test_present_tax_asserts_against_none(self):
        case = Case(
            name="x",
            document="doc",
            gold=Gold(category="Meals", total=1.0, n_items=1, tax_is_none=False),
        )
        assert "this.tax != none" in render_case(case)


class TestCoversTheCorpus:
    def test_every_case_becomes_a_test_block(self):
        rendered = render()
        for case in CORPUS:
            assert f"test {case.name} {{" in rendered

    def test_every_case_asserts_all_four_dimensions(self):
        for case in CORPUS:
            block = render_case(case)
            assert "@@assert(category" in block
            assert "@@assert(total" in block
            assert "@@assert(line_items" in block
            assert "tax" in block

    def test_gold_values_reach_the_assertions(self):
        case = Case(
            name="x",
            document="doc",
            gold=Gold(category="Hardware", total=2182.8, n_items=2, tax_is_none=False),
        )
        block = render_case(case)
        assert '== "Hardware"' in block
        assert "== 2182.8" in block
        assert "|length == 2" in block

    def test_documents_are_embedded_verbatim(self):
        case = Case(
            name="x",
            document="LINE ONE\nLINE TWO",
            gold=Gold(category="Other", total=1.0, n_items=1, tax_is_none=True),
        )
        block = render_case(case)
        assert "LINE ONE" in block and "LINE TWO" in block

    def test_output_carries_a_do_not_edit_banner(self):
        assert "DO NOT EDIT" in render()
