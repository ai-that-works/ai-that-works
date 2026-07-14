Hello {firstName},

This week's 🦄 ai that works session was on agent observability. Vaibhav's opening point set the tone: he doesn't read most of the code he ships anymore, and he thinks most of us are heading there too. If you're not reading every line, the only way left to understand what your system is actually doing is to watch it after it runs.

The full recording is on [YouTube](https://www.youtube.com/watch?v=_WLVv1C6-VM), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-07-07-agent-observability).

**Observability only pays off in hindsight, so the instrumentation has to already be there.** Vaibhav's framing: you can't have foresight about a bug. If you already knew where it was, you'd just fix it. The whole value of tracing is that when a user reports something broken, you can go back and look instead of trying to reproduce it blind. That means the tracing has to be in the code before the bug happens, not added after.

**The better your system gets, the more "red" you'll see, and that's not a sign something's wrong.** As agents get more capable, user expectations climb faster than the system does. The gap between what people think your agent can do and what it can actually do keeps growing, and every time a user runs into that gap, you get a red mark. Vaibhav's point: don't read rising error counts as your system getting worse. Read them as your users pushing harder against a boundary that used to be invisible.

**Wide, structured events beat plain OpenTelemetry, because OTel forces you to flatten everything into strings.** OTel only accepts strings, booleans, numbers, and simple sequences of those. So most teams end up doing `json.dumps()` on anything complex, shipping it as a blob, and losing the ability to query it. Vaibhav's team measured this: turning 100 bytes of real data into a JSON string can balloon it to 800 bytes over the wire, which is a real hit to latency and cost once you're tracing everything.

**Type your traces the same way you type your code, so an agent can query them like a database.** The goal Vaibhav showed live: something like `user.images.generate_image where args.thing.length > 50 and latency > 1s`. For a query like that to work, the trace has to know that the input argument is a string and the output is an image, the same way your code does. Once traces carry that shape, an agent can write its own queries against production behavior instead of you writing custom log-grepping scripts every time something breaks.

**Trace the full spectrum: design, code, and execution, and feed what you learn back into the next round.** Dex and Vaibhav sketched this as a loop. You trace during planning (Dylan's habit of asking Claude Code to show him call stacks before he approves a plan). You trace while the code exists (understanding a function by watching its flame graph instead of reading every line it calls). And you trace after it runs in production. The payoff comes when you close the loop: feed the execution trace back to the model and ask what was missing from the design that made the real call stack diverge from what you'd planned.

**If you remember one thing from this session:**

Instrument by default, not by exception. Vaibhav's advice was blunt: trace every fetch call, capture every LLM input and output, and automatically redact the risky stuff (headers, env vars, API keys) so you're not making a judgment call about what to log every time you write a function. If an agent is writing most of your code, it's not going to remember to add tracing every single time unless the system does it for it. And if you don't have that data when something breaks, you have zero chance of debugging it after the fact.

**Next session: SOTA Coding Agent Benchmarks, July 14th**

We've had benchmarks for coding agents for a long time. This week Vaibhav and Dex dig into the last generation versus the new one: what's actually different, what the numbers are missing, and where the next round of benchmarks needs to go. Sign up here: https://luma.com/sota-benchmarks

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
