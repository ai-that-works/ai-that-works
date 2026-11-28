# 🦄 ai that works: No Vibes Allowed: Shipping in the Opus 5.5 Era

> This week on the podcast we're hosting another session of our No Vibes Allowed series, where we skip the slides and write real code, live, to solve real problems. In this episode, Dex demos his new workflow for shipping software in the era of Opus 5.5, and Vaibhav shares what his team is doing at BAML.

[Video](https://www.youtube.com/watch?v=a3T9Du5rOvo)

[![You're Not Using AI to Its Full Potential… Here's How to Change That](https://img.youtube.com/vi/a3T9Du5rOvo/0.jpg)](https://www.youtube.com/watch?v=a3T9Du5rOvo)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-11-24-no-vibes-opus-5-5)

## Episode Highlights

> "Just because the model did a thing and it looks good from the outside does not mean it's perfect."

> "Instead leverage downtime to have the model show you things."

> "What I choose to work on is the most important decision I make every day."

> "Before doing something correctly, you can just half-ass do it."

> "Why am I waiting 30 to 60 seconds for an inference turn in between every question?"

## Key Takeaways

- **Give your main chat three jobs, and use the downtime to read code.** Vaibhav's main thread drives subagents, shows him things, and tracks important versus urgent. While a subagent works, he has the model show him suspicious code, which is how he caught a concurrency design that took 10x the instructions it needed. Without that, you wander off, come back lazy, and accept whatever default the model chose.
- **Experiments are cheap, so run more of them.** Vaibhav's team ported Pi to BAML file by file knowing it would be slop. Aaron built a demo that fingerprints each test by its dependencies, so changing a divide-by-100 to divide-by-10 marks exactly which tests are dirty. Reflection and network calls poison everything above them, so those tests always run.
- **Put an orchestrator in front of your subagents.** Instead of a main chat spawning read-only subagents, Dex chats with an orchestrator that launches interactive top-level agents for each phase. About 80% of his chatting happens with the orchestrator, and he steps into a subagent when a task needs lots of back and forth. Vaibhav landed on about the same ratio.
- **You probably don't need a skill pack.** Skills used to inject as user messages, which models followed more closely than tool results. Newer models don't need that, so Dex keeps one skill with reference files, mostly output templates like how to slice and describe a PR. When he tells an agent the same thing three times, he updates the skill.
- **Let the model write the plan with decisions already made.** In Lucas Meyer's L-Plan flow, each decision is filled in with a recommendation and alternatives sit in collapsed sections. Say "for D3, do B instead" and the model keeps decisions one and two and redoes everything below three.
- **Be ambitious and be skeptical.** Ask the model for things you don't think it can do, then verify. Understanding what it's doing is what lets you answer its long questions instead of accepting defaults.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=a3T9Du5rOvo)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

