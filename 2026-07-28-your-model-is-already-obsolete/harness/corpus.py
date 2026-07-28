"""The anchor set: hand-labelled cases, gold determined by the policy.

Gold labels here are not opinions. Every one is derivable from the policy
in `baml_src/expense.baml`, which is why a model that disagrees is wrong
rather than merely different.

Cases are weighted toward CATEGORY BOUNDARY decisions, because measurement
showed that is the only dimension where models actually differ.

30 cases. `HOWTO.md` calls 30 the magic number for basic coverage; below
that a single case swings the pass rate too far to gate on.

EVERY gold label here must be derivable from the policy in
`baml_src/expense.baml`. If you add a case whose label rests on your own
judgement, you have reintroduced the "your label is wrong, not the model"
problem the policy exists to prevent — either extend the policy or drop
the case.

Cases come in deliberate PAIRS that pull the precedence rule in opposite
directions, so a model cannot pass by learning a shortcut:

  * hotel_folio / room_service_exceeds_room   — lodging vs food
  * monitor_on_software_invoice / software_from_hardware_vendor — vendor trap
  * catering_beats_venue / event_ticket_beats_catering — food vs event fee
  * conference_pass / conference_plus_bigger_hotel — Other vs Travel

TWO THINGS LEARNED WHILE AUTHORING THESE, both worth knowing before you
add more:

1. LINE ORDER MATTERS. `catering_beats_venue` failed 1-in-4 runs with the
   room-hire line first: the model settled on a category and then dropped
   the line that did not match it. Putting the dominant line FIRST made it
   100% over 4 runs. If a case is flaky on `line_items`, try reordering
   before you blame the model.

2. A FLAKY CASE BREAKS A ZERO-TOLERANCE GATE. With
   `max_accuracy_drop=0.0`, a case that flips run-to-run makes the
   baseline itself noisy, so the gate fails candidates at random. Fix the
   case or widen the budget — do not leave it.

Note the incumbent does NOT score 100%: it fails `office_coffee_supplies`
3/3, insisting on Other where the policy says food and drink is Meals.
That is a real, deterministic incumbent failure and it is kept on purpose.
A baseline that is already perfect leaves a candidate no room to be
better, and "the model you are being pushed off was never flawless" is
worth saying out loud.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gold:
    category: str
    total: float
    n_items: int
    tax_is_none: bool


@dataclass(frozen=True)
class Case:
    name: str
    document: str
    #: `None` for unlabelled documents on the differential path, where
    #: two models are compared to each other rather than to an answer.
    gold: Gold | None
    #: Why this case exists. Shown on stage when it goes red.
    rationale: str = ""


CORPUS: list[Case] = [
    Case(
        name="hotel_folio",
        document="""THE LANGHAM - FOLIO 4471
Room, 2 nights @ 189.00 ............ 378.00
Breakfast, 2 @ 24.50 ................ 49.00
Subtotal ........................... 427.00
Occupancy tax (12%) ................. 51.24
Amount charged ..................... 478.24""",
        gold=Gold(category="Travel", total=478.24, n_items=2, tax_is_none=False),
        rationale=(
            "Mixed lodging + meals. Policy: categorise by largest line item, "
            "so room (378.00) wins and this is Travel. Tempting wrong answers "
            "are Meals and Other."
        ),
    ),
    Case(
        name="conference_pass",
        document="""RE:WORK CONFERENCE - RECEIPT 2210
Conference pass, 1 @ 899.00 ........ 899.00
Workshop add-on, 1 @ 150.00 ........ 150.00
Subtotal .......................... 1049.00
TOTAL ............................. 1049.00
(no tax collected)""",
        gold=Gold(category="Other", total=1049.00, n_items=2, tax_is_none=True),
        rationale=(
            "Policy states conference and event fees are Other, never Travel. "
            "Without the policy this label would be arguable; with it, "
            "'Travel' is objectively wrong."
        ),
    ),
    Case(
        name="saas_no_tax",
        document="""CLOUDSPEND LTD - INVOICE 88214
Item                          Qty   Unit      Amount
Datadog seat licence            3   42.00     126.00
Terraform Cloud add-on          1   19.50      19.50
--------------------------------------------------
Subtotal                                     145.50
TOTAL DUE                                    145.50
No tax applied (reverse charge).""",
        gold=Gold(category="Software", total=145.50, n_items=2, tax_is_none=True),
        rationale="Optional-field trap: tax must be omitted, not emitted as 0.0.",
    ),
    Case(
        name="monitor_on_software_invoice",
        document="""JETBRAINS RESELLER - INV 5512
IntelliJ licence renewal, 1 @ 599.00 .... 599.00
Dell U2723QE monitor, 2 @ 610.00 ....... 1220.00
Subtotal .............................. 1819.00
VAT 20% ................................ 363.80
Total ................................. 2182.80""",
        gold=Gold(category="Hardware", total=2182.80, n_items=2, tax_is_none=False),
        rationale=(
            "Software vendor, but the largest line is physical goods. Policy: "
            "Hardware regardless of vendor, categorise by largest line. "
            "Vendor name is the trap."
        ),
    ),
    Case(
        name="client_dinner",
        document="""OSTERIA FRANCESCANA
Table 12 - 4 covers
Tasting menu, 4 @ 210.00 ........... 840.00
Wine pairing, 2 @ 95.00 ............ 190.00
Subtotal ......................... 1030.00
Service 12% ....................... 123.60
TOTAL ............................ 1153.60""",
        gold=Gold(category="Meals", total=1153.60, n_items=2, tax_is_none=True),
        rationale=(
            "Service charge is NOT tax under the policy, so tax must be "
            "omitted. Tests that the model distinguishes a government tax "
            "from a gratuity instead of stuffing any trailing percentage "
            "into the tax field."
        ),
    ),
    Case(
        name="rail_and_sandwich",
        document="""TRAINLINE - BOOKING TL88301
London -> Edinburgh, 1 @ 142.50 .... 142.50
Onboard sandwich, 1 @ 6.50 .......... 6.50
Subtotal ........................... 149.00
TOTAL .............................. 149.00
No VAT on rail travel.""",
        gold=Gold(category="Travel", total=149.00, n_items=2, tax_is_none=True),
        rationale=(
            "Meals-during-travel rule vs largest-line rule. Rail (142.50) "
            "dominates, so Travel. Checks the model applies the tie-break "
            "rather than fixating on the word 'sandwich'."
        ),
    ),

    # ---- TRAVEL: transport and lodging only ----
    Case(
        name="flight_with_baggage",
        document="""BRITISH AIRWAYS - E-TICKET 125-4478213
LHR -> JFK economy, 1 @ 612.00 ..... 612.00
Checked bag, 2 @ 65.00 ............. 130.00
Subtotal ........................... 742.00
Air passenger duty ................. 194.00
Total charged ...................... 936.00""",
        gold=Gold(category="Travel", total=936.00, n_items=2, tax_is_none=False),
        rationale="Air passenger duty is a government tax. Largest line is transport.",
    ),
    Case(
        name="airport_taxi_with_tip",
        document="""CITY CABS - RECEIPT 99120
Airport transfer, 1 @ 78.00 ......... 78.00
Driver gratuity, 1 @ 12.00 .......... 12.00
Subtotal ............................ 90.00
TOTAL ............................... 90.00
No tax charged on this fare.""",
        gold=Gold(category="Travel", total=90.00, n_items=2, tax_is_none=True),
        rationale="Gratuity is not tax under the policy. Transport is the larger line.",
    ),
    Case(
        name="hotel_with_booking_fee",
        document="""TRAVELODGE - CONFIRMATION 55813
Room, 3 nights @ 92.00 ............. 276.00
Booking fee, 1 @ 14.00 .............. 14.00
Subtotal ........................... 290.00
TOTAL .............................. 290.00
No tax applicable.""",
        gold=Gold(category="Travel", total=290.00, n_items=2, tax_is_none=True),
        rationale="Booking fee is explicitly not tax. Lodging dominates.",
    ),
    Case(
        name="conference_plus_bigger_hotel",
        document="""EVENTBRITE COMBINED INVOICE 7741
Summit ticket, 1 @ 340.00 .......... 340.00
Hotel, 4 nights @ 155.00 ........... 620.00
Subtotal ........................... 960.00
TOTAL .............................. 960.00
No tax collected.""",
        gold=Gold(category="Travel", total=960.00, n_items=2, tax_is_none=True),
        rationale=(
            "Precedence rule in tension with the conference rule. Hotel "
            "(620.00) is the larger line, so Travel wins over Other."
        ),
    ),
    Case(
        name="rail_season_ticket",
        document="""NATIONAL RAIL - SEASON 40218
Monthly season ticket, 1 @ 388.00 .. 388.00
Subtotal ........................... 388.00
TOTAL .............................. 388.00
Rail travel is zero-rated.""",
        gold=Gold(category="Travel", total=388.00, n_items=1, tax_is_none=True),
        rationale="Single-line control case. Zero-rated is not a tax amount.",
    ),

    # ---- MEALS: food and drink, even during travel ----
    Case(
        name="room_service_exceeds_room",
        document="""HOTEL FOLIO 8871 - EXTENDED STAY
Room, 1 night @ 110.00 ............. 110.00
Restaurant charges, 6 @ 48.00 ...... 288.00
Subtotal ........................... 398.00
City tax ............................ 31.84
TOTAL .............................. 429.84""",
        gold=Gold(category="Meals", total=429.84, n_items=2, tax_is_none=False),
        rationale=(
            "Inverts hotel_folio: food (288.00) beats lodging (110.00), so "
            "the precedence rule makes this Meals, not Travel."
        ),
    ),
    Case(
        name="team_lunch_with_vat",
        document="""DISHOOM - TABLE 22
Sharing platters, 6 @ 34.00 ........ 204.00
Soft drinks, 6 @ 4.50 ............... 27.00
Subtotal ........................... 231.00
VAT 20% ............................. 46.20
TOTAL .............................. 277.20""",
        gold=Gold(category="Meals", total=277.20, n_items=2, tax_is_none=False),
        rationale="Unambiguous. VAT is a real government tax.",
    ),
    Case(
        name="office_coffee_supplies",
        document="""PACT COFFEE - ORDER 31182
Coffee beans 1kg, 4 @ 22.00 ......... 88.00
Oat milk case, 2 @ 15.50 ............ 31.00
Subtotal ........................... 119.00
TOTAL .............................. 119.00
Zero-rated food items.""",
        gold=Gold(category="Meals", total=119.00, n_items=2, tax_is_none=True),
        rationale="Food and drink is Meals even when it is office supply.",
    ),
    Case(
        name="catering_beats_venue",
        document="""OFFSITE INVOICE 2288
Buffet lunch, 20 @ 27.00 ........... 540.00
Room hire, 1 @ 250.00 .............. 250.00
Subtotal ........................... 790.00
VAT 20% ............................ 158.00
TOTAL .............................. 948.00""",
        gold=Gold(category="Meals", total=948.00, n_items=2, tax_is_none=False),
        rationale="Room hire is Other; catering (540.00) is larger, so Meals.",
    ),

    # ---- SOFTWARE: regardless of vendor ----
    Case(
        name="cloud_bill",
        document="""AMAZON WEB SERVICES - INVOICE 448120
EC2 compute, 1 @ 1840.00 .......... 1840.00
S3 storage, 1 @ 212.00 ............. 212.00
Subtotal .......................... 2052.00
VAT 20% ............................ 410.40
TOTAL ............................. 2462.40""",
        gold=Gold(category="Software", total=2462.40, n_items=2, tax_is_none=False),
        rationale="Control case for Software with tax.",
    ),
    Case(
        name="domain_renewal_no_tax",
        document="""NAMECHEAP - RECEIPT 71230
Domain renewal .com, 3 @ 11.98 ...... 35.94
Privacy guard, 3 @ 2.88 .............. 8.64
Subtotal ............................ 44.58
TOTAL ............................... 44.58
No tax collected for this region.""",
        gold=Gold(category="Software", total=44.58, n_items=2, tax_is_none=True),
        rationale=(
            "Policy explicitly counts domains and hosting as Software — "
            "without that line the label would rest on taste. Also checks "
            "decimal handling on small amounts."
        ),
    ),
    Case(
        name="software_from_hardware_vendor",
        document="""DELL BUSINESS - INVOICE 90441
Windows Server licence, 4 @ 470.00 . 1880.00
USB-C dock, 1 @ 189.00 ............. 189.00
Subtotal .......................... 2069.00
VAT 20% ............................ 413.80
TOTAL ............................. 2482.80""",
        gold=Gold(category="Software", total=2482.80, n_items=2, tax_is_none=False),
        rationale=(
            "Mirror of monitor_on_software_invoice. Hardware vendor, but "
            "licences (1880.00) dominate, so Software. Vendor is the trap."
        ),
    ),
    Case(
        name="saas_with_onboarding",
        document="""SEGMENT - INVOICE 6612
Annual platform licence, 1 @ 12000.00 . 12000.00
Onboarding services, 1 @ 2500.00 ...... 2500.00
Subtotal ............................. 14500.00
Sales tax 8.875% ...................... 1286.88
TOTAL ................................ 15786.88""",
        gold=Gold(category="Software", total=15786.88, n_items=2, tax_is_none=False),
        rationale="Large values; licence dominates the one-off service fee.",
    ),

    # ---- HARDWARE: physical goods regardless of vendor ----
    Case(
        name="laptop_purchase",
        document="""APPLE STORE - RECEIPT 5512093
MacBook Pro 14, 1 @ 1999.00 ....... 1999.00
Subtotal .......................... 1999.00
VAT 20% ............................ 399.80
TOTAL ............................. 2398.80""",
        gold=Gold(category="Hardware", total=2398.80, n_items=1, tax_is_none=False),
        rationale="Single-line control case for Hardware.",
    ),
    Case(
        name="peripherals_bundle",
        document="""KEYCHRON DIRECT - ORDER 88213
Mechanical keyboard, 3 @ 108.00 ..... 324.00
Wireless mouse, 3 @ 42.00 .......... 126.00
Subtotal ........................... 450.00
TOTAL .............................. 450.00
Import duty prepaid, no VAT charged.""",
        gold=Gold(category="Hardware", total=450.00, n_items=2, tax_is_none=True),
        rationale="'Duty prepaid' is a distractor — no tax amount is shown.",
    ),
    Case(
        name="monitor_with_warranty",
        document="""CDW - INVOICE 33901
LG UltraFine 32, 2 @ 749.00 ....... 1498.00
3-year warranty, 2 @ 89.00 ......... 178.00
Subtotal .......................... 1676.00
Sales tax 6% ....................... 100.56
TOTAL ............................. 1776.56""",
        gold=Gold(category="Hardware", total=1776.56, n_items=2, tax_is_none=False),
        rationale="Warranty is a service, but the monitors dominate.",
    ),

    # ---- OTHER: conference, training, and things no rule covers ----
    Case(
        name="training_course",
        document="""PLURALSIGHT LIVE - RECEIPT 4471
Kubernetes intensive, 2 @ 1450.00 .. 2900.00
Subtotal .......................... 2900.00
TOTAL ............................. 2900.00
No tax applied.""",
        gold=Gold(category="Other", total=2900.00, n_items=1, tax_is_none=True),
        rationale=(
            "Training fee is Other by policy. A model may be tempted by "
            "Software because the subject is technical."
        ),
    ),
    Case(
        name="coworking_day_passes",
        document="""WEWORK - INVOICE 20114
Day pass, 12 @ 29.00 ............... 348.00
Subtotal ........................... 348.00
VAT 20% ............................. 69.60
TOTAL .............................. 417.60""",
        gold=Gold(category="Other", total=417.60, n_items=1, tax_is_none=False),
        rationale=(
            "Not lodging and not transport, so not Travel. No other rule "
            "applies, so Other."
        ),
    ),
    Case(
        name="event_ticket_beats_catering",
        document="""TECH SUMMIT - INVOICE 9931
Delegate passes, 4 @ 495.00 ....... 1980.00
Lunch add-on, 4 @ 38.00 ............ 152.00
Subtotal .......................... 2132.00
TOTAL ............................. 2132.00
No tax collected.""",
        gold=Gold(category="Other", total=2132.00, n_items=2, tax_is_none=True),
        rationale=(
            "Inverse of catering_beats_venue. Event fee (1980.00) dominates "
            "the food, so Other rather than Meals."
        ),
    ),
    Case(
        name="recruitment_fee",
        document="""HAYS RECRUITMENT - INVOICE 71129
Placement fee, 1 @ 8500.00 ........ 8500.00
Subtotal .......................... 8500.00
VAT 20% ........................... 1700.00
TOTAL ............................ 10200.00""",
        gold=Gold(category="Other", total=10200.00, n_items=1, tax_is_none=False),
        rationale="Nothing in the policy covers recruitment, so Other.",
    ),

    # ---- tax-field edge cases ----
    Case(
        name="zero_tax_stated_explicitly",
        document="""OFFICE DEPOT - RECEIPT 11823
Desk lamp, 2 @ 34.50 ................ 69.00
Subtotal ............................ 69.00
Tax .................................. 0.00
TOTAL ............................... 69.00""",
        gold=Gold(category="Hardware", total=69.00, n_items=1, tax_is_none=False),
        rationale=(
            "Deliberate inverse of the usual trap: the document DOES show a "
            "tax line that happens to read 0.00, and the policy says to "
            "report an explicit tax line even at zero. Distinguishes 'no "
            "tax line' from 'a tax line of zero' — a distinction the first "
            "draft of the policy got wrong, demanding 0.00 while also "
            "forbidding it."
        ),
    ),
    Case(
        name="service_charge_and_real_tax",
        document="""THE IVY - TABLE 8
Set menu, 5 @ 62.00 ................ 310.00
Subtotal ........................... 310.00
Service charge 12.5% ................ 38.75
VAT 20% ............................. 62.00
TOTAL .............................. 410.75""",
        gold=Gold(category="Meals", total=410.75, n_items=1, tax_is_none=False),
        rationale=(
            "Both a service charge AND a real tax. tax must be 62.00, not "
            "100.75. Hardest tax case in the corpus."
        ),
    ),
    Case(
        name="tax_inclusive_pricing",
        document="""BERLIN CAFE - BELEG 4412
Mittagsmenu, 3 @ 18.00 .............. 54.00
Subtotal ............................ 54.00
enthaltene MwSt 19% ................. 10.26
GESAMT .............................. 54.00""",
        gold=Gold(category="Meals", total=54.00, n_items=1, tax_is_none=False),
        rationale=(
            "Tax-inclusive pricing: total equals subtotal because the tax is "
            "already inside it. Tests that the model does not add the tax on "
            "top. Foreign-language labels are a secondary distractor."
        ),
    ),
    Case(
        name="discount_before_tax",
        document="""FIGMA - INVOICE 88120
Org seats, 20 @ 45.00 ............... 900.00
Annual discount, 1 @ -90.00 ......... -90.00
Subtotal ........................... 810.00
Sales tax 8% ........................ 64.80
TOTAL .............................. 874.80""",
        gold=Gold(category="Software", total=874.80, n_items=2, tax_is_none=False),
        rationale="Negative line item. Checks the model keeps the sign.",
    ),
]

BY_NAME = {c.name: c for c in CORPUS}
