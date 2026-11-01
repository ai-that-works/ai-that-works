# 🦄 ai that works: SlopCodeBench: The New Metrics

> Dex walks through the latest SlopCodeBench results across model families and effort levels, then Vaibhav shows how baking maintainability rules and metrics into BAML gives coding agents back pressure on code quality. A short one, but dense.

[Video](https://www.youtube.com/watch?v=VLonoD9m4VY)

[![Why Opus Medium Beats X-High at Writing Maintainable Code](https://img.youtube.com/vi/VLonoD9m4VY/0.jpg)](https://www.youtube.com/watch?v=VLonoD9m4VY)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-10-27-slopcodebench-new-metrics)

## Episode Highlights

> "If you just do the lights off factory thing and just feed a model features and high-level design, you will over time accumulate so much slop."

> "Some of these bigger, juicier models, if you ask them to think more, they will think themselves out of the right solution."

> "Many people now would sacrifice a little bit of cost in favor of maintainability."

## Key Takeaways

- **Strict pass rate is the number to watch.** A checkpoint only counts if its tests and every earlier checkpoint's tests pass. If checkpoint one shipped a bug, no later checkpoint can earn a strict pass, which mirrors how real bugs behave. In the latest run, Astra edged out Opus 5.5.
- **More effort doesn't reliably buy better code.** Opus 5.5 on medium beat Opus 5.5 on x-high by about three percentage points for less money, while the OpenAI models did better on x-high. Fable 5.1 on x-high was the expensive outlier with little to show for it. Run your own tasks at two effort levels before changing your team's default.
- **Counting slop means counting the trash the model leaves behind.** Test scripts and verifier files stay in the metrics, because if you merge without looking and the model never cleans up, that mess is part of the slop. Vaibhav's team bans stray `.md` files in the repo for the same reason: they go stale, then the next agent reads them as truth.
- **The detectors are aggressive and aging.** Around 212 slop detectors mix custom AST linters with standard metrics like cyclomatic complexity, and many date from March and May. Opus 5.5 x-high triggered the fewest, while Fable wrote nearly the most functions with the lowest average complexity, which says nothing yet about whether anyone would want to read them.
- **Put maintainability rules in the compiler, not just the prompt.** Vaibhav wrote guidelines from good and bad examples (no magic numbers, `match` over `if/else`), ran each task from scratch ten times, and saw nearly every complexity metric improve, with the worst function's cyclomatic complexity the holdout. Having the compiler push back when code got worse is cheap back pressure.
- **Optimize for maintainability months from now, not for today's cost.** Tokens and agent time matter far less than complexity that compounds. Turn your own style rules into a skill or check, run the same task with and without them, and see in a chart whether they actually simplify the code.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=VLonoD9m4VY)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

