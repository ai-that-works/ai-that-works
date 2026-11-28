Hello {firstName},

This week's 🦄 ai that works session was another No Vibes Allowed, on how Dex and Vaibhav ship software in the Opus 5.5 era. We hit some technical difficulties, so Dex's live build turned into a walkthrough of his setup, and Vaibhav filled the first half with demos of what his team is doing at BAML.

The full recording is on [YouTube](https://www.youtube.com/watch?v=a3T9Du5rOvo), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-11-24-no-vibes-opus-5-5).

**Give your main chat three jobs, and use the downtime to read code.** Vaibhav's main thread drives subagents, shows him things, and tracks what's important versus urgent. While a subagent grinds on a task, he has the model show him suspicious or interesting parts of the codebase. That's how he caught a concurrency design that took 10x the instructions it needed, and default parameters that were designed wrong. If you don't fill that gap, you'll wander off to Twitter, come back lazy, and accept whatever default decision the model made while you were gone. Dex's addition: be ambitious, but stay skeptical. Ask the model for things you don't think it can do, then verify.

**Experiments are cheap now, so run more of them.** Vaibhav's team rewrote their compiler in BAML to see what would happen, and ported Pi to BAML file by file knowing the code would be slop. Aaron built a demo that fingerprints every test by the functions and classes it depends on. Change a divide-by-100 to divide-by-10 and it marks exactly which tests are dirty. Reflection or a network call poisons everything above it, so those tests always run. It's pure slop code, and that's fine, because the point was to learn what's possible before designing the real thing.

**Put an orchestrator in front of your subagents.** The old model was one main chat spawning read-only subagents you never talk to. Dex now chats with an orchestrator that launches top-level, interactive agents for each phase of research, design, and plan. You stop deciding which skill to run and when to start a fresh context window. When he wants to dig into decision three, the orchestrator fires off a new agent to research it, and his main conversation stays clean. About 80% of his chatting happens with the orchestrator, and he steps into a subagent when a task needs a lot of back and forth. Vaibhav landed on roughly the same ratio independently.

**You probably don't need a skill pack.** Skills used to inject their contents as a user message, which models followed more closely than a tool result. Newer models don't need that. Dex sometimes just says "clone that repo, read the skill file, and do it." He keeps one skill, with everything else as reference files, and mostly fills it with output templates: how a PR should be sliced and described, how to show him a diff. Anytime he tells an agent the same thing three times, he opens a side chat and says "update the skill so this doesn't happen again." Vaibhav does the opposite and changes his own phrasing instead.

**Let the model write the plan with decisions already made.** In Lucas Meyer's L-Plan flow, the model writes a plan doc where every decision is filled in with its recommendation, and the alternatives sit in collapsed sections. You read top to bottom. If you disagree with decision three and say "do B instead," the model treats one and two as accepted and redoes everything below three. Dex's reasoning: if you agree with 80% of the recommendations anyway, why wait 60 seconds between every question?

**If you remember one thing from this session:**

Be ambitious and be skeptical, and let the same habit serve both. Tell the main chat to keep showing you code while the subagents work, so you understand the problem well enough to question the answers. Before your next big task, add this line to your prompt: "While you work, show me parts of the code I should look at." Then read them.

**Next session: Building Evals on Production Data, Tuesday (December 1st) at 10 AM PT**

We've done a lot of eval design and framework deep dives. This time we get practical about taking production data and using it to design and extend your eval system. Sign up here: https://luma.com/evals-on-prod-data

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
