Hello {firstName},

This week's 🦄 ai that works session was a second trip into SlopCodeBench, this time with its creator. Gabe Orlanski from UW Madison joined Dex and Vaibhav to walk through the qualitative side of the data: which slop patterns are fading, which are getting worse, and what agents do when you ask them to design a library.

The full recording is on [YouTube](https://www.youtube.com/watch?v=3WSxv4vzLhM), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-11-17-emergent-slop-behaviors).

**The old slop is going away. The new slop is harder to see.** Line-level patterns are dropping across every model family. Returning `None` plus an error tuple is mostly gone. OpenAI models took `sys.exit` down to zero. But Gabe's point is that the slop moved up the stack. It now shows up in dependencies and error handling. For example, a model now raises more errors, which is better, but the message says "sources not tabular CSV content" and gives you no clue which row is broken. That kind of problem passes every linter and still costs you an afternoon.

**Agents avoid libraries and rewrite them inline.** Even with full internet access, agents refuse to install libraries that would make the job easier. When they do try something, you get `try: import foo` with a hand-written fallback that re-implements the whole library in the except branch. Check your own agent's diffs for this. If you see a fallback that is longer than the thing it replaces, tell the agent to pick one dependency and use it.

**Agents also copy the shape of existing libraries without thinking about who will use theirs.** In the LibraryDesignBench setup, agents design a library and other agents are scored on how well they use it. Gabe's guidance to the designing agents was to ship runnable examples instead of docs, keep every function name as short as possible, and test with subagents over and over. The result was simpler code from agents consuming it. If your library will mostly be called by agents, a folder of copy-pasteable templates probably beats a README.

**Weird patterns are creeping back in.** The new patterns Gabe flagged include Python 2 style checks like `type(x) == T` instead of `isinstance`, and a pile of defensive `if x is None` guards. Vaibhav's theory is that models got burned by the subtle difference (`isinstance` walks the inheritance tree, `type` doesn't) and that the habit is being trained in from earlier generations. Gabe's counter: the best Python he has read is built so that those guards are never needed. Both agree it's a sign models learn from the previous generation's slop.

**Tests can become part of the slop.** Gabe's biggest pet peeve is tests that pin an implementation so tightly that a later checkpoint can't centralize or refactor without breaking them. The agent then hyperfixates on keeping the old code alive. Vaibhav's workaround on rewrites: first commit deletes the old feature and its tests. Then replan. Then reimplement. Without the old code in context, there is nothing for the model to bias toward preserving.

**If you remember one thing from this session:**

Stop judging agent code by whether it looks like what a human would write. Judge it by whether the next agent can fix a bug in it without reverse engineering the whole repo. Dex's version: slop is only bad if it undermines the goal. A pattern humans dislike but agents handle well is fine. A pile of pinned tests and hand-rolled library clones is not. Before your next merge, ask one question: if a fresh agent had to change this tomorrow, would it have to fight the code?

**Next session: No Vibes Allowed: Shipping in the Opus 5.5 Era, tomorrow (November 24th) at 10 AM PT**

We skip the slides and write real code live. Dex demos his new workflow for shipping software with Opus 5.5, including the new skills and setup he has been using day to day. Sign up here: https://luma.com/no-vibes-opus-55

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
