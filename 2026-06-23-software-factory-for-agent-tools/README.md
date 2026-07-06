# 🦄 ai that works: Software Factory for Agent Tools

> Building a persistent 24/7 feedback loop that tests new BAML language features using coding agents and improves the language based on what they struggle with.

[Video](https://www.youtube.com/watch?v=485FGIq8LKM)

[![Software Factory for Agent Tools](https://img.youtube.com/vi/485FGIq8LKM/0.jpg)](https://www.youtube.com/watch?v=485FGIq8LKM)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-06-23-software-factory-for-agent-tools)

## Episode Highlights

> "We realized no matter how good tests we write, no matter how much work we do, it doesn't work."

> "We don't have to actually go decide this. Instead of waiting for humans to report these issues after a lot of work, we can just have it write code that humans are gonna write anyway."

> "There's a level of detail that agents are really good at and there's a level of detail that humans are really good at."

> "Go do this for yourself. It'll probably make your product better. Way faster than you will."

> "You don't have to build the entire software factory at once. You can build small. Find places where you can use agents, figure out where are the right leverage points for humans, where are the right leverage points for agents, and then just start building those things and plugging them into each other."

## Key Takeaways

- **The core loop is simpler than it looks.** An agent tries to implement something, the system captures the chat log, a second agent analyzes what went wrong (they call the output a "trophy"), deduplicates findings across runs, and files a Linear ticket with a repro and suggested fix. Then a separate agent opens a PR. That's it. What makes it powerful is that it runs nightly on the latest release without anyone scheduling it.
- **Agents surface bugs humans would never think to look for.** One run found that BAML's CLI was parsing negative numbers as command-line flags, so `baml run -e "code with -7 in it"` would break in a completely non-obvious way. Vaibhav's first reaction was that it had to be a hallucination. It wasn't. These are the bugs that never appear in a neatly filed issue.
- **There are two separate loops, each with a max turn limit.** The issue loop runs until an issue is human-approved. The PR loop runs until checks pass or max turns hit. Cursor agents open PRs immediately without running the local test suite, letting GitHub CI handle it instead. That dropped test time from fifteen to twenty minutes down to two to four.
- **The human's job is to decide what counts, not to write code.** Humans read issues, decide if they're real, and steer direction. Vaibhav left one comment on a ticket saying "this is a BAML describe issue, not a skill issue." The agent rewrote the ticket accordingly. That back-and-forth is the only human work required before a PR opens.
- **You can A/B test your documentation the same way you test code.** Their "arena" runs the same tasks against multiple versions of the BAML skill (the docs given to agents) and measures cost, turns, and success rate. The shortest skill often beats the longest one because `baml describe` does the heavy lifting at runtime.

## Resources

## Resources

- [Session Recording](https://www.youtube.com/watch?v=485FGIq8LKM)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
