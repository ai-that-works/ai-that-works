Hello {firstName},

This week's 🦄 ai that works session was on coding agent benchmarks, and Vaibhav opened with a blunt take: code is asymptotically approaching total slop, no matter what you do or where you do it. The rest of the session was Vaibhav and Dex working through why the benchmarks we use to grade coding agents can't actually catch that.

The full recording is on [YouTube](https://www.youtube.com/watch?v=X5mI1ZVxaIc), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-07-14-sota-coding-agent-benchmarks).

**Benchmarks measure "did it pass the test," not "did it write good code."** Dex walked through Terminal-Bench and SWE-bench: a model gets a GitHub issue, checks out the code at that commit, writes a fix, and a verifier checks if the test passes. There's no penalty for a model that wraps everything in unnecessary try/catch blocks or does a weird double typecast to force the test green. You could write a linter for one specific pattern like that, but not a general one, because sometimes that same "ugly" code is actually the right call.

**One viral benchmark measures almost the wrong thing entirely.** Vaibhav walked through Terminal-Bench's sibling, a benchmark that anonymizes an open-source binary and tells the model "mimic this program, one to one," with zero other context. Models score close to zero on it, which is why it went viral. But as Vaibhav put it, software isn't about mimicking a binary. It's about solving the problem your users actually have, and adapting the code as that problem changes. A benchmark that rewards exact replication is measuring something almost backwards from real engineering.

**The newest benchmarks add a judge model and a quality judge, not just pass/fail.** Frontier Code, the most advanced one they walked through, has an "adjudicator" model compare the agent's code against a human-written golden patch, plus a separate quality judge that checks the code against a list of quality rules. It even runs mutation testing: it strips out the agent's code changes and checks whether the agent's own tests still fail against the old code. If they don't, the agent wrote tests that don't actually test anything, which is exactly the kind of test suite that quietly slows a team down for months.

**No benchmark can catch the bug that shows up six months later.** Dex's core argument: the damage from a bad architectural pattern doesn't show up when the code ships. It shows up when three other features get built on top of the same bad pattern, and *then* something breaks. To train a model to avoid that, you'd need a verifier that can score decisions made months before the consequence happens, across millions of training runs. Nobody has built that, and Vaibhav isn't sure anyone can, since even senior engineers usually can't verbalize why a piece of code will age badly. They just say "it feels funny."

**If you remember one thing from this session:**

The models are getting much better at solving one-off tickets, and much slower to improve at maintaining a codebase over time, because that's the only thing current benchmarks can actually score. Vaibhav's practical takeaway: find where your team can insert a small amount of human judgment (an intuition about how a piece of code needs to evolve) so that the rest of the problem looks, to the model, like the one-shot ticket it's already great at solving.

**Next session: No Vibes Allowed, July Edition, July 21st**

Another round of our No Vibes Allowed series, where we take everything we've been talking about and show it running in real code against real problems. Sign up here: https://luma.com/no-vibes-jul-26

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
