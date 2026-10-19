Hello {firstName},

This week's 🦄 ai that works session was a deep dive into a memory pipeline that the HumanLayer and Boundary teams built together. Aaron (co-founder and CTO of Boundary) joined Dex to walk through how it reads your team's coding agent sessions and turns them into proposed changes to your CLAUDE.md: what agents keep getting stuck on, what humans keep correcting, and the tribal knowledge that never makes it into the repo.

The full recording is on [YouTube](https://www.youtube.com/watch?v=mAKUL12h1n8), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-10-06-building-a-memory-pipeline).

**The first version was "directionally correct" and really bad.** Dex's original pipeline stripped out the tool calls, sent the user and assistant messages to a single Haiku structured output call, and got back a list of "context shards," each with the memory, the reasoning, and a citation back to the session and message. Some findings were good. Most needed another round of prompt tweaking. And cutting all the tool calls to save money threw away a lot of the signal, while Haiku 4.5 still wasn't that cheap.

**Split the pipeline by where the learning comes from.** Aaron's version runs three tracks. One extracts small facts agents found out along the way. One catches humans correcting the agent, like a teammate telling the agent "we don't have relative namespaces." The third looks at what subagents were sent to research, maps every file they read into a heat map of the codebase, and asks which docs actually answered the question. Facts that show up across sessions get grouped into one memory. One question about how BAML built-ins are organized came up in 11 sessions from two different people.

**Use a classifier to throw away most of the data before a big model sees it.** Jev scores every message ("is the agent trying to discover something here?", "is this a correction or just 'do phase six'?") and only what survives goes on to Opus for grouping and judging. The pattern is weak model, strong model, weak model, strong model. Jev filtering kept 60% of the text but 100% of the messages from the golden set, and Aaron put it at roughly 5% of the bill. The finished pipeline ran a week of his team's sessions for about two cents per session.

**Start with the most expensive version, then distill it.** Aaron's first report came from just pointing Claude Code at the raw session data. That cost around $100 for a report the final pipeline produces for about 50 cents. It was worth it. He watched which messages Claude filtered and which scripts it wrote, used that run as the golden dataset, and measured every later prompt change against it.

**Build tools so you can iterate fast, and read every prompt yourself.** The dashboard in the demo is version 10 of one of about ten dashboards he built. Every LLM call is cached by hashing its inputs, so you can rerun step five without paying for steps one through four. The dashboards sit on BAML query, which stores every call from a run in a SQLite database your agent can query with plain SQL to build whatever UI you need. And asking Claude Code to print every prompt is how he caught a bug where long messages were cut off at the end. The fix was to cut out the middle instead, so you keep both the opening and the conclusion. Dex's rule: anything in a prompt that you didn't write yourself came out of the model's weights, so it adds nothing.

**If you remember one thing from this session:**

The best memory isn't always a new fact. When Aaron gave the pipeline access to the repo, it found that agents kept asking how the codebase was laid out because nobody told them to read the existing `architecture.md`. The fix was one line in CLAUDE.md pointing to that file, not a pile of new facts. Before you add 200 one-fact skills, hand the report to an agent in your repo and ask it how to fix the root cause.

**Next session: Software Factory Debate, October 20th**

Zach, CTO of Warp, has strong opinions on software factories and how to get the most out of agentic coding. Dex agrees with him on most of it but maybe not all of it. Vaibhav is moderating with a whiteboard, so expect it to get spicy. Sign up here: https://luma.com/software-factory-debate

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
