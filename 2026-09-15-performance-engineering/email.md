Hello {firstName},

This week's 🦄 ai that works session had Vaibhav joined by Kai (Boundary's runtime engineer) and Tomás Senart, a fifteen-year performance engineering veteran now building PerfLoop, to talk about what happens when you point coding agents at nanosecond-level optimization instead of typical feature work.

The full recording is on [YouTube](https://www.youtube.com/watch?v=WHLXRZi8Mus), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-15-performance-engineering).

**Performance work has a design loop and an implementation loop, and agents are only good at one of them.** Vaibhav's take: models struggle badly with incremental changes that require holding two states of a system in mind at once, like a telemetry system that works today next to the leaner one you're replacing it with. Ask an agent to "make it better" without deleting the old path first, and it'll quietly leave a dead field around, an extra addition nobody needs, a copy of the old bad pattern because it saw it nearby in the file. The fix that worked: run a delete-only pass first, force every trace of the old system out, then start a fresh context window and say "now make this faster." Separating the two loops keeps the model from reverting to legacy patterns it can still see in front of it.

**When you're chasing sub-100-microsecond precision, your own tooling becomes the bottleneck.** Kai and Vaibhav both pointed out that once you need that level of timing precision, you can't run other work trees, Chrome, or basically anything else on the same machine while you measure, or the noise wrecks your numbers. Vaibhav's workaround: block off time where the only thing running is the benchmark, and do design docs or planning work instead of any other coding during that window. If your team doesn't have spare machines to isolate for this, that's worth fixing before you try to optimize anything below the millisecond range.

**Boundary's actual telemetry trick: give every core its own slice of IDs instead of coordinating on every single one.** They wanted a unique span ID for every function call without paying for a UUID mint (tens to hundreds of nanoseconds) on every call. The fix was a shared 64-bit counter that each CPU core grabs in chunks of 4096 IDs at a time, then increments locally until it runs out and needs to sync again. That turns an expensive atomic operation into a cheap local increment for the vast majority of calls, only paying the coordination tax once every few thousand IDs instead of on every one.

**Context management for high-stakes edits looks less like chatting and more like annotation.** Vaibhav described moving away from the terminal for anything performance-critical, because one wrong assumption in a hot loop costs him days of work. Instead of side-chats (which are UI-expensive and easy to lose), he annotates directly in the code, asks a read-only side agent clarifying questions when he's unsure about something, and every ten or so messages has the model restate every key decision and struct it's made so far, purely to keep the important details fresh even if the harness compresses context later.

**Performance engineering is basically the inverse of security: you have to win every single time, not just some of the time.** Tomás framed both fields as hypothesis-driven, you propose something, then prove or refute it empirically, but with an asymmetry. In security, an agent can go broad, find some vulnerabilities, and still add value even if it misses others, because the defender only loses once. With performance, missing one hot spot tanks the whole optimization effort, so breadth from parallel agents matters less than depth on the one thing that's actually slow.

**If you remember one thing from this session:**

Vaibhav's closing line was "do less work, that's the one takeaway," but the more actionable version is this: before you hand an agent a performance problem, separate deletion from construction. Have it rip out the old path completely, verify it's gone, and only then ask it to build the faster version in a clean context. Trying to do both at once is how you end up with a system that's neither the old design nor the new one.

**Next session: All About Jev, September 22nd**

Jev has been making waves in the AI world this week. We're digging into how token generation might be holding back your agent architecture, how jev compares to and complements BAML, and why generating text for routing and classification is often an antipattern when a fast decision model would do. Sign up here: https://luma.com/all-about-jev

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
