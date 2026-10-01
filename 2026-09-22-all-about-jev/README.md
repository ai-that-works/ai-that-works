# 🦄 ai that works: All About Jev

> Jev has been making lots of waves in the AI world this week. This week on the podcast, we will dive into jev and discuss how token generation may be holding back your agent architecture and how jev compares to and complements BAML. We'll look at what type safety means across different layers of the stack, why generating text for routing and classification is an antipattern, and how to combine fast decision models with BAML-orchestrated workflows for production agent architecture.

[Video](https://www.youtube.com/watch?v=35PSMmDDKP8)

[![Jev Explained: The Fast AI Model We Tried to Break on Purpose](https://img.youtube.com/vi/35PSMmDDKP8/0.jpg)](https://www.youtube.com/watch?v=35PSMmDDKP8)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-22-all-about-jev)

## Episode Highlights

> "Output tokens in Jev are free because they're literally only outputting one token. It can't give you reasoning. It can't help you write an email, but it can still do a lot of things that LLMs were previously used for."

> "If you take the Jev philosophy, it's basically a state transition model. It gives you the next state if you can define the state in that way."

> "We're not always looking to model max. We're mostly looking to design max."

## Key Takeaways

- **Jev doesn't generate text, it hands you probabilities for options you define.** It supports three output shapes: choices (enums or unions of literals), scores (a rubric like "0 means X, 4 means Y"), and nools (yes/no questions). Classifying a message as happy or sad returns something like `{happy: 0.8, sad: 0.2}`. It only emits one token, so output tokens are free. It can't write an email, but it can decide what to do about one.
- **Any LLM call that outputs one word today is worth testing against Jev.** Router agents and classifiers are the obvious targets. Rippling's growth engineering team got 90% accuracy against a 50% LLM baseline while running 8x faster. Spend a couple of hours running your existing eval against it and look at cost and latency.
- **Fast, cheap classification changes what your code looks like.** Vaibhav built a BAML library where every type gets a `.feels()` method backed by Jev, so "while the draft feels full of corporate jargon, keep rewriting" becomes a real loop. His `grep_with_vibes` runs a feeling check on every line of stdin in parallel: pipe `git log` through it with "this would be scary to revert" and it surfaces the GC-related commits.
- **You can model a coding agent as a state machine, but the action space gets tight fast.** Dex's code search harness tracked "files read so far" as state and let Jev pick the next action, like `read_dir apps` or `read_file components/foo.ts`. Jev can't generate arguments, and it caps out around 255 options and 32K input tokens. That meant limiting each step to about 80 files and having the harness rank what to offer next. Dex called it "absolutely an abuse of Jev."
- **A smaller, faster model still needs a harness around it.** Jev will sometimes be wrong, like any small model. In a voice agent, for example, you run the fast loop up front and add a watchdog agent that reads the main agent's context and steers it back when it goes off track.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=35PSMmDDKP8)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
