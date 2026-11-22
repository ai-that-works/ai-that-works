# 🦄 ai that works: Emergent Behaviors with Gabe Orlanski, creator of SlopCodeBench

> Gabe Orlanski from UW Madison joins Vaibhav and Dex to dig into what's underneath the SlopCodeBench data: new slop patterns emerging or worsening in modern models like Fable and Opus 5.5, how agents do at building and designing libraries and interfaces, and what Dex and Vaibhav are doing to fight slop.

[Video](https://www.youtube.com/watch?v=3WSxv4vzLhM)

[![Emergent Behaviors with Gabe Orlanski, creator of SlopCodeBench](https://img.youtube.com/vi/3WSxv4vzLhM/0.jpg)](https://www.youtube.com/watch?v=3WSxv4vzLhM)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-11-17-emergent-slop-behaviors)

## Episode Highlights

> "Slop is only bad if it undermines our goal."

> "Agents refuse to ever install libraries that would make their lives easier."

> "The biggest piece of slop I've seen is tests that cause agents to hyperfixate on keeping old code around."

> "Delete it, that's the first commit, then re-implement it. Otherwise it will bias towards keeping the old stuff around by accident."

> "Our benchmarks need to fundamentally ask how far away we are from letting agents do everything."

## Key Takeaways

- **The old slop is fading, but the new slop is higher in the stack.** Line-level patterns like returning `None` plus an error tuple are mostly gone, and OpenAI models took `sys.exit` to zero. The problem moved into dependencies and error handling, like a raised error that says "sources not tabular CSV content" and never tells you which row is broken.
- **Agents rewrite libraries instead of using them.** Even with full internet access, they avoid installing dependencies, and you see `try: import foo` with a hand-written fallback that re-implements the whole library in the except branch.
- **Design libraries for the agents that will call them.** In LibraryDesignBench, agents were told to ship runnable examples instead of docs and keep function names as short as possible. Agents consuming those libraries wrote simpler code. Agents building libraries mostly copy the shape of existing human-oriented ones.
- **Weird patterns are creeping back in.** Python 2 style checks like `type(x) == T` instead of `isinstance` and piles of defensive `if x is None` guards keep showing up. Vaibhav's theory is that models got burned by the difference (`isinstance` walks the inheritance tree, `type` doesn't) and the habit got trained in from previous generations.
- **Over-specific tests are slop too.** Tests that pin an implementation stop later checkpoints from centralizing or refactoring, because the agent hyperfixates on keeping them green. Vaibhav's workaround on rewrites: delete the old feature and its tests in a first commit, replan, then reimplement.
- **Judge slop by whether the next agent can work with it.** A pattern humans dislike but agents handle well is fine. A codebase a stronger model has to reverse engineer just to reproduce a bug is not.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=3WSxv4vzLhM)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

