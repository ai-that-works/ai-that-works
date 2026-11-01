Hello {firstName},

This week's 🦄 ai that works session was a short one on the new SlopCodeBench results. Dex walked through the latest runs across model families and effort levels, then Vaibhav showed how his team turned maintainability metrics into back pressure for coding agents in BAML.

The full recording is on [YouTube](https://www.youtube.com/watch?v=VLonoD9m4VY), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-10-27-slopcodebench-new-metrics).

**Strict pass rate is the number to watch.** SlopCodeBench hands a model a spec, then keeps changing the requirements across 3 to 8 checkpoints, with about 36 challenges and 196 checkpoints in total. A strict pass means the current checkpoint's tests and every earlier checkpoint's tests all pass. If checkpoint one shipped with a bug, you can't get a strict pass at checkpoint four, which is how real bugs behave. In the latest run, Astra actually edged out Opus 5.5, even though Dex says Opus 5.5 is still his favorite model to work with.

**More effort doesn't always buy better code.** Opus 5.5 on medium beat Opus 5.5 on x-high by about three percentage points, and it cost less. Both hosts already default to medium (or low) for most work, since big models can think themselves out of the right answer. The OpenAI models went the other way: x-high cost more but scored better. Fable 5.1 on x-high was the expensive outlier, with a lot of spend and not much to show for it. So before you flip your whole team to the highest setting, run your own tasks at two effort levels and compare.

**Counting slop means counting the trash the model leaves behind.** Dex wanted to exclude test scripts and verifier files from the code quality numbers. Gabe, the researcher behind the benchmark, said no: if you merge without looking and the model never cleans up after itself, that mess is part of the slop. Vaibhav's team has the same rule. They don't allow stray `.md` files in the repo, because a temporary markdown file goes stale, then the next agent reads it as truth. Garbage scripts work the same way. Once one gets checked in, the model decides that's an acceptable pattern.

**The detectors are aggressive, and they're aging.** The benchmark has around 212 slop detectors, a mix of custom AST linters built from real AI-written repos and standard metrics like cyclomatic complexity. Many of them date from March and May, so newer models may have been trained out of some patterns. Opus 5.5 x-high triggered the fewest, but Dex cautions that doesn't mean the rest are bad code. Fable wrote nearly the most functions with the lowest average complexity, which looks great until you remember nobody has read that code yet. Gabe plans to look for which slop patterns are new and which are gone.

**Put the maintainability rules in the compiler, not just the prompt.** Vaibhav showed what happens when you write guidelines from examples of good and bad code (no magic numbers, `match` over `if/else`, filter and map over hand-built lists) and feed them to the model as a skill. They ran each task from scratch ten times, on projects like a chess move generator, a GTFS departures tool, and a regex engine. Nearly every complexity metric got better with the guidelines, with the worst function's cyclomatic complexity the one holdout. Then they went further and let the compiler push back when the code got worse. That is back pressure, and it doesn't cost much to add.

**If you remember one thing from this session:**

Optimize for how maintainable the code is a few months from now, not for how fast or cheap the agent finished today. Tokens and agent time matter far less than complexity that compounds. You should be able to take your own style rules, turn them into a skill or a compiler check, run the same task ten times with and without them, and see in a chart whether your rules actually make the code simpler. Vaibhav wants to try the same setup on SlopCodeBench itself, so expect a follow-up.

**Next session: Building Evals on Production Data, November 10th at 10 AM PT**

There will be no episode on November 3rd. When we're back, we'll get practical about taking your production data and using it to design and extend your eval system. Sign up here: https://luma.com/evals-on-prod-data

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
