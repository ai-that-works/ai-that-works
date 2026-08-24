
# 🦄 ai that works: syncs and A/B testing 200 agents

> A two-part episode: Avery from Boundary on why AI agents keep picking bad data structures (and how that compounds into slop), then Kyle Mistele from HumanLayer on how their sync engine keeps hundreds of live coding agent sessions in sync across web, mobile, and desktop clients.

[Video](https://www.youtube.com/watch?v=GF7dnSlCM4U) (58m39s)

[![syncs and A/B testing 200 agents](https://img.youtube.com/vi/GF7dnSlCM4U/0.jpg)](https://www.youtube.com/watch?v=GF7dnSlCM4U)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-08-18-syncs-and-ab-testing-200-agents)

## Episode Highlights

> "Show me your flowcharts and conceal your tables and I shall continue to be mystified. Show me your tables and I won't usually need your flowcharts, they'll be obvious."

> "If you've chosen the right data structures and organized things well, the algorithms will almost always be self-evident."

> "Bad programmers worry about the code. Good programmers worry about the data structures and the relationships."

> "One out of those ten is gonna make my codebase worse in a way that compounds. That means after a hundred features, my codebase will be like 40% slop."

> "It's always a skill issue, apparently. Either the agent's skill or your skill, but it's always a skill issue."

> "Sync engine is a fancy way to say real-time database."

> "The thing which you are perceiving as slow cancellation is us waiting for the daemon to finish flushing the events. One of the cool things we do have in our sync system is optimistic mutations, and the reason that feels slow to you is because we're not doing one there."

## Key Takeaways

- **Agents default to the convenient data structure, not the correct one, and it shows up immediately.** Avery ran 200 trials of Codex building a Ticketmaster clone one feature at a time, no memory between runs, same setup as SlopCodeBench. For "seats can be open, sold, or held," a chunk of runs used two boolean flags instead of a single enum, which means the code can represent a seat that's both held and sold at once, a state that should be impossible.
- **The right data structure was staring everyone in the face, and 40% of runs still missed it.** For "list seats in stable printable order," 35% of runs used a self-balancing tree that keeps things ordered automatically. But 40% bolted on a separate array just to track ordering, a second source of truth that can silently drift from the real data.
- **A 12.5% bad-decision rate per feature compounds into a wrecked codebase.** On the trickiest feature (five-minute checkout holds), 12.5% of runs introduced a second source of truth for time tracking, with all tests still green. Dex's math: at that rate, after 100 features shipped you're looking at something closer to 40% slop, not 12.5%.
- **Building your own sync engine looks like building a chat app until you hit "shape churn."** A chat app only needs to sync an append-only list of messages. A coding agent's session needs any of a hundred different slices of state ("shapes"), and those shapes update every couple seconds while the agent runs. The hard part was never write volume, Postgres handles that fine, it's detecting what changed and figuring out which connected clients actually care.
- **HumanLayer runs two sync paths on purpose: one through Postgres, one that skips it entirely.** Structured data (tasks, sessions, conversation history) goes through Postgres's write-ahead log, so the sync engine tails it like a read replica. Token-by-token streaming, sometimes dozens of updates a second, would hammer Postgres for no reason, so that path goes straight through a separate durable stream server backed by SQLite and a flat file log.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=GF7dnSlCM4U)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://luma.com/software-factory-design)

## Whiteboards

