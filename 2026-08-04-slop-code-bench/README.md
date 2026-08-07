# 🦄 ai that works: SlopCodeBench

> Most coding benchmarks hand a model the whole spec up front and grade the first draft. SlopCodeBench doesn't. It hands a model checkpoint one, waits, then hands it checkpoint two on top of whatever the model just built, then three, then four, up to eight checkpoints deep, and asks: does it still pass everything, or did it bury itself in its own slop?

[![SlopCodeBench](https://img.youtube.com/vi/Yh4eL60Ncxs/0.jpg)](https://www.youtube.com/watch?v=Yh4eL60Ncxs)

## The idea

Dex walks through SlopCodeBench, a benchmark by Gabe Orlanski (University of Wisconsin-Madison) that's explicitly designed to stay hard and unsaturated: today's frontier models top out around 33% strict pass rate, which is SWE-bench-2024 territory. Every challenge starts as a small spec (e.g. build a JQ-like tool for XML) and grows new requirements every checkpoint (add CSS selectors, then JSON support, then file I/O), so the model inherits and has to keep extending its own prior code instead of solving a fixed problem once.

Two pass rates matter, and the gap between them is the whole point:

- **Isolated pass rate** - did the model solve the current checkpoint?
- **Strict pass rate** - did it solve the current checkpoint *and* keep every previous checkpoint passing?

A model can nail checkpoint four and still fail strict pass if it quietly broke checkpoint three along the way. That's the real-world failure mode SlopCodeBench is built to catch: not "can it write code" but "does it accumulate a mountain of slop that makes every future checkpoint harder."

## What the data showed

- **Spending more money correlates with fewer defects, but it's not a clean win.** Fable beat Sonnet on strict pass rate by about 2 percentage points, at roughly 5x the cost.
- **All the frontier models cluster together on code-quality metrics** (cyclomatic complexity, duplicated lines, dependency entropy) despite very different pass rates. Vaibhav's read: there's less alpha in "which model" than people assume, and more in problem definition and harness design.
- **Only Sonnet wrote actual Python unit tests.** Every other model tested its own code with ad hoc scripts, seemingly because the first checkpoint set the pattern and later checkpoints just followed it.
- **95% of Sonnet's generated code triggered at least one of SlopCodeBench's ~200+ Python AST-based "slop detectors."** Dex's caveat: a high trigger rate doesn't necessarily mean bad code, the detectors are aggressive by design, but it's a real signal for comparing models against each other.
- **Planning didn't move the needle.** SlopCodeBench tested "just solve it" against "plan, then implement" and found close to no difference. Dex's theory: writing a plan used to be a trick to get a model to work unattended for longer; now that models are RL'd to just keep going, that specific benefit of planning has mostly evaporated.

## Where the conversation went next

Vaibhav's challenge to the benchmark: give the model every checkpoint's spec up front instead of drip-feeding them, and see if pass rate jumps. His hypothesis is that the best engineers succeed by predicting the future accurately, not by iterating blind, so a model that gets the whole picture early might just do better. Dex hadn't tried that comparison and is planning to add it.

They also traded takes on when a "lights off, no humans in the loop" signal would actually be trustworthy:

1. Give the model the full spec up front and compare against the incremental version.
2. After a checkpoint, hand the same codebase to a *smaller* model and see if it can ace the next checkpoint unassisted. If a frontier model's code is clean enough that GPT-OSS-120B can build on it correctly, that's a real signal of maintainability.
3. Add deterministic linting/complexity caps as a feedback loop during the run, the way real teams already gate PRs with CI.

## On skills and AGENTS.md going stale

The conversation closed on Boris Cherney's advice to throw out your AGENTS.md and skills every time a new model ships. Vaibhav's take: delete them by default, and put the burden on the team to justify keeping any of them. Dex's framing for what survives that cut: skills should carry *information* the model can't know on its own (your repo's type system quirks, which subfolder of a monorepo actually matters, that your main branch is called `canary`), not *instructions* for things models already do reliably (running tests, using the GitHub CLI). Instructional skills are the ones that quietly rot and start detuning a model's default behavior once it's already good at the task.

## Key Takeaways

- **Strict pass rate is the number that matters, not isolated pass rate.** A model can solve every new checkpoint and still fail strict pass if it quietly broke an earlier one along the way. For example, GPT-5.4 Codex won on isolated pass rate by solving more individual challenges, but Opus 4.6 won on strict pass rate by fixing things without regressing what already worked.
- **Today's best models only hit 33% strict pass rate, so the benchmark isn't saturated yet.** Sonnet 5 and Fable tied at 33%, GPT-5.5 came in at 14.8%. Spending more money correlated with fewer defects but not cleanly: Fable beat Sonnet by about 2 points on strict pass rate while costing roughly 5x as much.
- **Only Sonnet wrote real unit tests, likely because of what happened on checkpoint one.** Every other model tested its own code with throwaway scripts instead of `pytest`. Dex's theory: whatever testing pattern gets set on the first checkpoint sticks, because the next checkpoint's context window sees "we test this with a script" and just keeps following that precedent.
- **Planning didn't move the needle, which surprised both hosts.** SlopCodeBench compared "just solve it" against "plan, then implement" and found almost no difference. Dex's read: planning used to work by keeping a model working unattended for longer instead of pausing to check in, and now that models are trained to just keep going, that specific benefit is mostly gone.
- **Skills should teach a model information it can't know, not instructions it already follows.** For example, "our type system requires X" or "only touch this monorepo subfolder unless told otherwise" belongs in a skill, because that's genuinely unknowable to the model. "Always run tests after a change" doesn't, since current models already do that by default, and keeping instructional skills like that around can actively detune a model that's already better than the skill assumes.

## Resources

- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
