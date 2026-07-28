"""Do the corpus documents add up? Pure arithmetic, no model involved.

Every other check on this corpus runs through an LLM, which means a shared
bias between the author and the model would go unnoticed. These tests are
the one independent authority: they parse the documents as text and verify
the numbers are internally consistent and that the gold matches what the
document actually says.

If a document is wrong here, every measurement taken against it is noise.
"""

from __future__ import annotations

import re

import pytest

from harness.corpus import CORPUS, Case

AMOUNT = re.compile(r"(-?\d[\d,]*\.\d{2})")
QTY_AT_UNIT = re.compile(r"(?:qty\s+)?(-?\d+)\s*(?:\w+\s+)?@\s*(-?\d[\d,]*\.\d{2})")

TOTAL_WORDS = ("total", "gesamt", "amount charged", "amount due", "total due")
SUBTOTAL_WORDS = ("subtotal",)
TAX_WORDS = ("vat", "sales tax", "occupancy tax", "city tax", "duty", "mwst", "tax")
NON_TAX_WORDS = ("service", "gratuity", "tip", "booking fee")


def _num(text: str) -> float | None:
    found = AMOUNT.findall(text)
    return float(found[-1].replace(",", "")) if found else None


def _classify(line: str) -> str:
    low = line.lower()
    # Line items are the only lines with a `qty @ unit` shape, and this
    # MUST be checked first: "Driver gratuity, 1 @ 12.00" is a line item,
    # not a service charge, even though it says gratuity. Checking the
    # keyword lists first silently drops such lines from the subtotal.
    if QTY_AT_UNIT.search(line) and not any(w in low for w in SUBTOTAL_WORDS + TOTAL_WORDS):
        return "item"
    if any(w in low for w in SUBTOTAL_WORDS):
        return "subtotal"
    if any(w in low for w in TOTAL_WORDS):
        return "total"
    if any(w in low for w in NON_TAX_WORDS):
        return "service"
    if any(w in low for w in TAX_WORDS) and AMOUNT.search(line):
        return "tax"
    if QTY_AT_UNIT.search(line):
        return "item"
    return "other"


def parse(case: Case) -> dict:
    items, subtotal, tax, total, service = [], None, None, None, None
    for line in case.document.splitlines():
        kind = _classify(line)
        value = _num(line)
        if kind == "item" and value is not None:
            qty, unit = QTY_AT_UNIT.search(line).groups()
            items.append((int(qty), float(unit.replace(",", "")), value))
        elif kind == "subtotal":
            subtotal = value
        elif kind == "tax":
            tax = value
        elif kind == "service":
            service = value
        elif kind == "total":
            total = value
    return {
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "service": service,
        "total": total,
    }


@pytest.mark.parametrize("case", CORPUS, ids=lambda c: c.name)
class TestDocumentsAddUp:
    def test_each_line_item_multiplies_out(self, case: Case):
        for qty, unit, line_total in parse(case)["items"]:
            assert abs(qty * unit - line_total) < 0.01, (
                f"{case.name}: {qty} @ {unit} should be {qty * unit:.2f}, "
                f"document says {line_total:.2f}"
            )

    def test_line_items_sum_to_subtotal(self, case: Case):
        parsed = parse(case)
        if parsed["subtotal"] is None or not parsed["items"]:
            pytest.skip("no subtotal line")
        got = sum(t for _, _, t in parsed["items"])
        assert abs(got - parsed["subtotal"]) < 0.01, (
            f"{case.name}: items sum to {got:.2f}, subtotal says {parsed['subtotal']:.2f}"
        )

    def test_gold_total_matches_the_document(self, case: Case):
        parsed = parse(case)
        if parsed["total"] is None:
            pytest.skip("no total line")
        assert abs(case.gold.total - parsed["total"]) < 0.01, (
            f"{case.name}: gold says {case.gold.total:.2f}, "
            f"document total line says {parsed['total']:.2f}"
        )

    def test_gold_line_item_count_matches_the_document(self, case: Case):
        parsed = parse(case)
        if not parsed["items"]:
            pytest.skip("no parseable line items")
        assert case.gold.n_items == len(parsed["items"]), (
            f"{case.name}: gold expects {case.gold.n_items} items, "
            f"document has {len(parsed['items'])}"
        )

    def test_gold_tax_flag_matches_the_document(self, case: Case):
        """A tax LINE must exist iff gold says tax is present.

        Catches the class of bug that made `zero_tax_stated_explicitly`
        demand a value the policy forbade.
        """
        parsed = parse(case)
        has_tax_line = parsed["tax"] is not None
        assert has_tax_line is (not case.gold.tax_is_none), (
            f"{case.name}: document {'has' if has_tax_line else 'has no'} tax line, "
            f"gold says tax_is_none={case.gold.tax_is_none}"
        )
