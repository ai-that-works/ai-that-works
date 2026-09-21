# 🦄 ai that works: Performance Engineering

> When milliseconds are too slow, you have to engineer for nanoseconds. This week, we're unpacking N5-level optimization for AI workloads and what it takes to shave off ultimate low-level latency. We discuss the engineering techniques required to strip away overhead, optimize memory throughput, and push inference infrastructure to absolute hardware limits.

[Video](https://www.youtube.com/watch?v=WHLXRZi8Mus)

[![Why Performance Engineering Breaks AI Coding Agents](https://img.youtube.com/vi/WHLXRZi8Mus/0.jpg)](https://www.youtube.com/watch?v=WHLXRZi8Mus)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-15-performance-engineering)

## Episode Highlights

> "Performance boils down to three things: do less work, use less memory, use caches better. If you squint, the last two are just versions of the first."

> "I don't personally think models are very good at incremental changes and maintaining two states of the system at the same time."

> "My only job is to read here and be like, is there anything fatal that's happening? If I catch a fatal mistake, and I know there's no fatal mistakes, I'm mostly good."

> "With security, the defender has to always win and the attacker only has to win once. With performance, you always have to win, every time, or the rest of your optimization work was pointless."

## Key Takeaways

- **Performance work has a design loop and an implementation loop, and agents are only good at one of them.** Models struggle to hold two states of a system in mind at once, like an old telemetry system next to the leaner one replacing it, and will quietly leave dead fields or copy old bad patterns nearby. The fix: run a delete-only pass first, verify the old code is gone, then start a fresh context window and ask for the faster version.
- **When you're chasing sub-100-microsecond precision, your own tooling becomes the bottleneck.** Running other work trees or even Chrome on the same machine wrecks timing measurements at that resolution, so the team blocks off dedicated windows where the only thing running is the benchmark, doing design docs or planning during that time instead.
- **Boundary's telemetry trick: give every core its own slice of IDs instead of coordinating on every single one.** Rather than minting a UUID (tens to hundreds of nanoseconds) per span, each CPU core grabs a chunk of 4096 IDs from a shared 64-bit counter and increments locally, paying the atomic coordination cost only once every few thousand calls instead of on every one.
- **Context management for high-stakes edits looks like annotation, not chat.** Instead of side-chats that are UI-expensive and easy to lose, annotate directly in the code, use a read-only side agent for clarifying questions, and have the model restate every key decision every ten or so messages to keep details fresh even through context compression.
- **Performance engineering is the inverse of security: you have to win every single time, not just some of the time.** Both are hypothesis-driven and empirical, but in security an agent going broad can still add value even if it misses some vulnerabilities, since the defender only loses once. In performance, missing one hot spot tanks the whole optimization effort, so depth on the one real bottleneck matters more than breadth across many agents.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=WHLXRZi8Mus)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
