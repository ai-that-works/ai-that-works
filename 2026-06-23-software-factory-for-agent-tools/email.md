Hello {firstName},

This week's 🦄 ai that works session was on software factories, and the actual thing Vaibhav and Dylan built is weirder and more practical than the name suggests. The short version: they have agents writing BAML code 24/7, watching where it breaks, filing issues, writing fixes, and opening PRs. Humans stay in the loop, but they're not the ones finding bugs or writing code anymore.

The full recording is on [YouTube](https://www.youtube.com/watch?v=485FGIq8LKM), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-06-23-software-factory-for-agent-tools).

**The core loop is simpler than you think.** An agent tries to implement something in BAML. It hits bugs. The system captures the full chat log, runs another agent to analyze what went wrong (they call the output a "trophy"), deduplicates findings across runs, and creates a Linear ticket with a repro and a suggested fix. Then a separate agent opens a PR. Then another agent responds to CodeRabbit comments and CI failures. The humans hit merge. That's the whole thing. What makes it powerful is that it runs nightly, on the latest release, without anyone scheduling it.

**Agents surface bugs humans would never think to look for.** One run found that BAML's CLI was parsing negative numbers as command-line flags, so `baml run -e "code with -7 in it"` would break in a completely non-obvious way. Vaibhav's first reaction was that it had to be a hallucination. It wasn't. Another run noticed that agents kept writing `$!` (the TypeScript non-null assertion operator) in BAML because BAML looks a lot like TypeScript, and the error message was useless. The fix: a specific compiler error that says "Unexpected exclamation mark. BAML has no non-null assertion operator. Unwrap optionals with question mark question mark default." These are the kinds of things a human never sits down to fix because the problem never surfaces in a clean way.

**There are two separate loops, and they have max turn limits.** The issue loop runs until an issue is human-approved. The PR loop runs until checks pass or max turns hit. Cursor agents open the PR immediately, without running the test suite locally, because Cursor's sandboxes were too slow. GitHub CI handles it instead. That dropped test time from fifteen to twenty minutes down to two to four. When the agent gets stuck after a set number of attempts, it moves the ticket to "needs human" and pings Slack. The human shows up, reads what went wrong, and decides whether to unstick it or close it.

**The human's job is to decide what counts.** Humans don't write code or find bugs. They read the issue, decide if it's real, and steer it in the right direction. Vaibhav gave a good example: an agent filed a ticket saying it was a skill issue (meaning the docs were wrong). He looked at it and said no, this is a BAML describe issue (meaning the language's introspection command should explain it better). He left a comment, set the status to redraft, and the agent rewrote the ticket according to his comment. That back-and-forth is the only human work required before a PR gets opened.

**If you remember one thing from this session:**

You do not have to build the whole factory. The redraft loop is just: agent drafts an issue, human adds a comment, agent redrafts. That is a complete, useful loop on its own. Stack a second loop on top when the first one is working. One day you will look up and realize that most of your bugs are being found, documented, fixed, and merged without you scheduling any of it. Start with the smallest isolated problem you have and build from there.

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
