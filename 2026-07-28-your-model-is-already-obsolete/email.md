Hello {firstName},

This week's 🦄 ai that works session was on model deprecation, and Kevin Gregory joined to show the harness he built to survive it. Six months ago Google announced Gemini 1.5 Flash's retirement date before Gemini 2.5 Flash had even shipped. That's the world we're in now: the replacement and the deadline arrive at the same time, and you're expected to just handle it.

The full recording is on [YouTube](https://www.youtube.com/watch?v=Y-I9m5YsAcs), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-07-28-your-model-is-already-obsolete).

**Obsolete and deprecated are different problems, and mixing them up makes teams complacent.** `gpt-4o` is the case study: it has no announced OpenAI retirement date, but it's been quietly de-listed from the models index, the comparison page, and the pricing page, while the endpoint keeps answering calls at $2.50/$10. Deprecated means there's a deadline on the calendar. Obsolete means something better already exists and nobody's forcing you to move, so nobody does. "It still works" stays true right up until the day it doesn't.

**The question isn't "is this model good," it's "is it worse than what I'm already running."** Kevin's framing: don't score a candidate model against some absolute accuracy bar, diff its outputs against your production model on the same test cases. If a new model agrees with the incumbent on 28 of 30 cases, you only need to hand-review the 2 where they disagree. That's how you build a real eval set without hand-labeling everything from scratch.

**A missing price defaulted to zero silently passed four out of five candidates.** This one bit the harness itself. When a model's cost data wasn't in the lookup table, the code defaulted it to `0.0`, so every unpriced candidate looked like it cost nothing and sailed through the cost gate. The fix wasn't a better default, it was refusing to judge at all when the price is unverified. A wrong number is worse than an honest "I don't know."

**Single-run evals produced two confidently wrong answers before anyone caught it.** These models aren't deterministic on the same input twice. Kevin found that running each test case once gave a clean, false signal about which model was better. The harness now runs three repeats per case by default, specifically because two separate conclusions during development turned out to be noise, not a real result.

**The regression budget is something you drag, not something you set once.** Live on the whiteboard, Kevin pulled up a table scoring candidate models on accuracy, latency, and cost against the incumbent, then changed the latency tolerance from budget-tight to "I'm okay with 3x slower" and watched two more models flip from fail to pass. When nothing strictly wins on every axis, that's the case for handing the frontier to an optimizer (the GEPA-style run from [the December prompt optimizer episode](https://github.com/hellovai/ai-that-works/tree/main/2025-12-16-prompt-optimizer)) instead of picking a winner by hand.

**If you remember one thing from this session:**

Model deprecation is one of the only outages that comes with advance notice, and most teams still treat it as an emergency. Kevin's point: build the harness before you need it; a swap should be "change one string, rerun the gate, go home," not a two-week scramble the week a provider sends the retirement email.

**Next session: SlopCodeBench, August 4th**

Most coding benchmarks score a single-shot solution against a spec, which tells you nothing about whether a model can maintain code it wrote six months ago. SlopCodeBench (SCBench) makes frontier models build on their own previous output across multiple checkpoints, closer to how software actually gets extended, refactored, and kept alive. Sign up here: https://luma.com/slop-code-bench

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
