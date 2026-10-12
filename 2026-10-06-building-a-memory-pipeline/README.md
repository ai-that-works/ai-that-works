# 🦄 ai that works: Building a Memory Pipeline

> We've discussed how to build memory supervisors and memory pipelines before, but in this episode we're going to dive into real code and make it happen with real problems and real constraints.

[Video](https://www.youtube.com/watch?v=mAKUL12h1n8)

[![Why AI Coding Agents Need a Memory Pipeline](https://img.youtube.com/vi/mAKUL12h1n8/0.jpg)](https://www.youtube.com/watch?v=mAKUL12h1n8)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-10-06-building-a-memory-pipeline)

## Episode Highlights

> "Anything that is in the skill or the prompt that you yourself did not write is by definition something that is already in the model weights."

> "It only kept 60% of the text, but it kept 100% of the data that was valuable."

> "If you're just in a single session, you're not able to make correlations across many sessions."

## Key Takeaways

- **The naive version was directionally correct and still really bad.** Stripping tool calls and sending user and assistant messages to a single Haiku structured output call produced "context shards" with a memory, reasoning, and a session/message citation. Some findings were good, but it took constant prompt tweaking, dropping tool calls threw away signal, and Haiku 4.5 still wasn't cheap.
- **Split the pipeline by where the learning comes from.** One track extracts facts agents found out, one catches humans correcting the agent (e.g. "we don't have relative namespaces"), and one maps every file subagents read into a codebase heat map and asks which docs answered their question. Facts that recur across sessions get grouped: one question about how BAML built-ins are organized came up in 11 sessions from two people.
- **Use a classifier to drop most of the data before a big model sees it.** Jev scores each message ("is the agent trying to discover something?", "is this a correction or just 'do phase six'?") and only survivors go to Opus for grouping and judging. Filtering kept 60% of the text but 100% of the golden-set messages, Jev was roughly 5% of the bill, and the pipeline ran about two cents per session.
- **Start with the most expensive version, then distill it.** Pointing Claude Code at raw session data cost around $100 for a report the final pipeline produces for about 50 cents. That run became the golden dataset every later prompt change was measured against.
- **Build tools to iterate fast, and read every prompt yourself.** Cache each LLM call by hashing its inputs so you can rerun step five without paying for steps one through four, and use `BAML query` to put every call in a SQLite database an agent can query to build bespoke dashboards. Printing every prompt is how Aaron caught long messages being cut off at the end; the fix was cutting the middle instead.
- **The best memory isn't always a new fact.** With repo access, the pipeline found agents kept asking how the codebase was laid out because nothing told them to read `architecture.md`. The fix was one line in `CLAUDE.md`, not 200 one-fact skills.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=mAKUL12h1n8)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
