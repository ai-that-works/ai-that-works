// The task. Structured extraction with deterministic validators — no
// LLM-as-judge anywhere in this repo's eval path.
//
// Measurement (54 calls, 3 repeats x 6 models) showed the ENUM is the only
// dimension that actually discriminates between models. The arithmetic and
// the nesting are solved for everyone. They stay as cheap checks; don't
// expect them to catch anything.

enum ExpenseCategory {
  Travel
  Meals
  Software
  Hardware
  Other
}

class LineItem {
  description string
  quantity int
  unit_price float
  total float @description("quantity * unit_price")
}

class Expense {
  vendor string
  category ExpenseCategory
  line_items LineItem[]
  subtotal float
  tax float?  @description("omit entirely if the document shows no tax")
  total float
}

// The policy is what makes the gold labels defensible.
//
// Without it, calling a conference pass "Other" is taste, and any failure
// we show is arguable — someone says "your label is wrong, not the model",
// and they're right. With a stated rule, a wrong answer is objectively
// wrong. This is also the concrete thing the optimizer repairs after a
// swap: make the prompt encode the policy well enough that the new model
// follows it.
template_string ExpensePolicy() #"
  Apply this expense policy exactly. It overrides your own judgement.

  CATEGORY
  - Travel covers transport and lodging ONLY.
  - Conference, event and training fees are Other, never Travel.
  - Food and drink is Meals, even during travel or billed to a hotel.
  - Software is Software regardless of which vendor invoiced it.
  - Domains, hosting and online subscriptions count as Software.
  - Physical goods are Hardware regardless of which vendor invoiced them.
  - Use Other only when no rule above applies.

  PRECEDENCE
  - When one document mixes categories, categorise the WHOLE expense by
    its largest line item by total. This rule OVERRIDES every category
    rule above. A hotel folio of room 378.00 and breakfast 49.00 is
    Travel, not Meals, because the room is the larger line.

  TAX
  - `tax` means GOVERNMENT tax only: VAT, sales tax, occupancy tax,
    passenger duty. Service charges, gratuities, tips and booking fees
    are NOT tax and must never appear in this field.
  - If the document shows an explicit tax line, report that amount — even
    when the amount is 0.00.
  - If the document shows NO tax line at all, omit `tax` entirely. Never
    invent a 0.00 where the document names no tax.
  - Prose such as "zero-rated", "no tax applied", "exempt", "no VAT
    charged" or "duty prepaid" is NOT a tax line. It names no amount, so
    omit `tax`.
  - Where a document shows both a service charge and a tax, report only
    the tax.
"#

function ExtractExpense(document: string) -> Expense {
  client IncumbentGPT4o
  prompt #"
    Extract the expense record from this document.

    {{ ExpensePolicy() }}

    {{ ctx.output_format }}

    {{ _.role('user') }}
    {{ document }}
  "#
}
