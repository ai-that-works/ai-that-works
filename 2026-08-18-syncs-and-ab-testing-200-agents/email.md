Hello {firstName},

This week's 🦄 ai that works session was a two-part recap from the AI That Works Unconference: Avery from Boundary on why agents keep picking bad data structures, then Kyle Mistele from HumanLayer on how their sync engine keeps hundreds of coding agent sessions live across web, mobile, and desktop clients at once.

The full recording is on [YouTube](https://www.youtube.com/watch?v=GF7dnSlCM4U), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-08-18-syncs-and-ab-testing-200-agents).

**Agents default to the convenient data structure, not the correct one, and it shows up immediately.** Avery ran an experiment: have Codex build a Ticketmaster clone one feature at a time, 200 runs per feature, no memory of what the last run did, same setup as SlopCodeBench. For "seats can be open, sold, or held," a chunk of runs used two boolean flags instead of a single enum. That means the code can represent a seat that's both held and sold at once, a state that should be impossible. If you're reviewing agent output, check whether a "shouldn't happen" state can actually be constructed. If it can, that's the bug waiting to ship.

**The right data structure was staring everyone in the face, and 40% of runs still missed it.** For "list seats in a stable printable order," 35% of runs used a self-balancing tree that keeps things ordered automatically. But 40% bolted on a separate array just to track ordering, a second source of truth that can drift from the real data. When you're reviewing a PR and see a parallel structure tracking something the primary structure could track itself, that's usually the tell that the model reached for the familiar pattern instead of the correct one.

**A 12.5% bad-decision rate per feature isn't a rounding error, it compounds into a wrecked codebase.** On the trickiest feature (five-minute checkout holds), 12.5% of runs introduced a second source of truth for time tracking, silently, with all tests still green. Dex's math: if 1 in 8 features makes your codebase worse in a way that compounds, after 100 features shipped you're not looking at a 12.5% slop codebase, you're looking at something closer to 40%. That's the real argument for reviewing data structures specifically instead of skimming the diff and trusting the tests.

**Building your own sync engine looks like building a chat app until you hit "shape churn."** Kyle's point: syncing a chat app is easy because the data barely changes, messages just append. Syncing a coding agent's session is different because a client might need any of a hundred different slices of state ("shapes"), and those shapes update every couple of seconds while an agent is running. The hard part was never write volume, Postgres handles that fine. It's detecting what changed and figuring out which of your connected clients actually care, in real time.

**HumanLayer runs two sync paths on purpose: one through Postgres, one that skips it entirely.** Structured data (tasks, sessions, conversation history) goes through Postgres's write-ahead log, so the sync engine tails it like a read replica and pushes incremental updates out. But token-by-token streaming, sometimes dozens of updates a second, would hammer Postgres for no reason, so that path goes straight through a separate durable stream server instead. If you're building anything with both "occasional structured writes" and "high-frequency streaming updates," don't force both through the same pipe.

**If you remember one thing from this session:**

Slop doesn't start with bad code, it starts with bad data structures. Every downstream bug, every awkward serialization, every "why does this state even exist" moment traces back to a representation decision made early and never revisited. Review the data structures first. The code review of the logic gets a lot easier once the shape underneath it can't lie.

**Next session: Software Factory Design Patterns, August 25th**

We're digging into the key interfaces of a modern software factory: what to buy versus build, what you should always own yourself, across compute, dev environments, harnesses, and orchestration. We'll get into how sessions, traces, artifacts, and plans all become first-class peers of code in the new system of record for software. Sign up here: https://luma.com/software-factory-design

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
