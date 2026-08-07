Hello {firstName},

This week's 🦄 ai that works session was on SlopCodeBench, a coding benchmark that Dex has been running and posting results from all summer. Vaibhav hadn't dug into the data himself yet, so the whole episode is him poking at Dex's brain live: what does this benchmark actually measure, and does it tell us anything real about which models write maintainable code.

The full recording is on [YouTube](https://www.youtube.com/watch?v=Yh4eL60Ncxs), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-08-04-slop-code-bench).

**Most benchmarks hand a model the whole problem up front. SlopCodeBench doesn't.** It gives a model a small spec, like "build a JQ-like tool for XML," lets it write code, then adds a new requirement on top: now support CSS selectors, now support JSON, now read from a file instead of stdin. Up to eight checkpoints deep, and the model has to keep extending code it wrote itself instead of getting a clean slate. That's closer to how real software actually gets built. You rarely know the whole spec on day one.

**There are two pass rates, and the gap between them is the whole point.** Isolated pass rate asks "did it solve this checkpoint." Strict pass rate asks "did it solve this checkpoint without breaking any of the checkpoints before it." A model can nail checkpoint four and still fail strict pass if it quietly broke checkpoint three getting there. For example, GPT-5.4 Codex won on isolated pass rate, meaning it solved more individual challenges, but Opus 4.6 won on strict pass rate, because it fixed things without regressing what already worked.

**Today's best models are only hitting 33% strict pass rate.** That's SWE-bench-2024 territory, which means this benchmark isn't saturated yet, unlike a lot of the coding benchmarks that models now blow past. Sonnet 5 and Fable both tied at 33%. GPT-5.5 came in at 14.8%. Spending more money did correlate with fewer defects, but not cleanly: Fable beat Sonnet by about 2 percentage points on strict pass rate while costing roughly 5x as much.

**Only one model wrote real unit tests, and it's probably because of what happened on checkpoint one.** Sonnet was the only model that wrote actual Python tests. Every other model tested its own code with throwaway scripts instead. Dex's theory: whatever pattern gets set on the first checkpoint sticks, because the next checkpoint's context window sees "we test this with a script" and just keeps doing that, the same way a human engineer inherits whatever pattern is already in the codebase.

**Planning didn't move the needle, which surprised both of them.** SlopCodeBench compared "just solve it" against "write a plan, then implement," and found almost no difference in the results. Dex's read: planning used to work because it kept a model working unattended for longer instead of pausing to check in. Now that models are trained to just keep going, that specific benefit is mostly gone. If your `CLAUDE.md` still says "always plan before implementing," that instruction may be doing less than you think.

**Skills should teach a model information it can't know, not instructions it already follows.** The conversation closed on when to keep a skill around versus deleting it every time a new model ships. Vaibhav's rule: for example, "our type system requires X" or "only touch this monorepo subfolder unless told otherwise" belongs in a skill, because that's genuinely unknowable to the model. "Always run the tests after a change" doesn't, because current models already do that by default. Keeping instructional skills like that around doesn't help, it can actively detune a model that's already better than the skill assumes.

**If you remember one thing from this session:**

Strict pass rate is the number that matters, not isolated pass rate. A model that solves every new feature but quietly breaks old ones isn't actually shipping working software, it's shipping a codebase that looks done and isn't. If you're grading a coding agent on anything, check whether your eval punishes regressions as hard as it rewards new features.

**Next session: Unconference Recap, August 11th**

We're hosting another unconference this Saturday, August 8th, bringing together some of the sharpest people building with AI right now. If you can't make it, tune into next week's session for the recap: what came up, what people are actually building, and what surprised us. Sign up here: https://luma.com/unconf-recap

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
