# 🦄 ai that works: SOTA Coding Agent Benchmarks

> A tour through the generations of coding agent benchmarks, from SWE-bench to Terminal-Bench to Frontier Code, and an honest look at why none of them can measure whether your codebase is turning to slop.

[Video](https://www.youtube.com/watch?v=X5mI1ZVxaIc)

[![SOTA Coding Agent Benchmarks](https://img.youtube.com/vi/X5mI1ZVxaIc/0.jpg)](https://www.youtube.com/watch?v=X5mI1ZVxaIc)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-07-14-sota-coding-agent-benchmarks)

## Episode Highlights

> "Our code is turning to shit. It's asymptotically approaching total slop, no matter what you do, where you do it."

> "Software is not about mimicking software. Software is about can you continuously solve the problem that the users are going to have with your software?"

> "It's not done when the code is done, it's not done when it's merged, it's not done when it's deployed. It's done when it's in users' hands shipping value."

> "If you cannot build a judge that is good at judging code quality, then the knowledge of code quality will never end up in the weights."

> "The faster and cheaper you can make your back pressure, the tighter that loop, whether it's a type checker, a linter, or a testing suite, the less likely you are to get off track."

## Key Takeaways

- **Benchmarks measure "did it pass the test," not "did it write good code."** A model that wraps everything in unnecessary try/catch blocks or does a weird double typecast to force a test green pays no penalty. You could write a linter to catch one specific case like that, but not a general one, since sometimes that same "ugly" code is actually correct.
- **A viral benchmark can measure almost the wrong thing.** One benchmark anonymizes an open-source binary and tells the model to "mimic this program, one to one," with zero other context, which is why models score close to zero on it. But software isn't about mimicking a binary; it's about solving the problem users actually have and adapting as that problem changes.
- **The newest benchmarks add a judge model and mutation testing, not just pass/fail.** Frontier Code has an "adjudicator" model compare the agent's code to a human-written golden patch, plus a separate quality judge, and it strips out the agent's code changes to check whether the agent's own tests still fail against the old code, catching test suites that don't actually test anything.
- **No benchmark can catch the bug that shows up six months later.** The damage from a bad architectural pattern doesn't show up when the code ships; it shows up after three other features get built on the same bad pattern. Training a verifier to catch that would require scoring decisions months before their consequences happen, across millions of runs, which nobody has built.
- **Models are getting much better at one-off tickets and much slower to improve at maintaining a codebase over time**, because that's the only thing current benchmarks can score. The practical move is finding where a small amount of human judgment can reshape a problem so it looks, to the model, like the one-shot ticket it's already great at solving.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=X5mI1ZVxaIc)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
