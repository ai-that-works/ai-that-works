Hello {firstName},

This week's 🦄 ai that works session was all about Jev, the "system one" model from the TypeSafe AI team that everyone's been texting us about. Vaibhav called in from the Big Island, Dex called in from an airport, and together they covered what Jev actually is, whether it can save you money, and how far you can push it before it breaks.

The full recording is on [YouTube](https://www.youtube.com/watch?v=35PSMmDDKP8), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-22-all-about-jev).

**Jev doesn't generate text. It hands you probabilities for options you define.** You give it text in and one of three output shapes: choices (think enums or unions of literals), scores (a rubric like "0 means X, 4 means Y"), or nools (a yes/no question). Ask it to classify a message as happy or sad and you get back something like `{happy: 0.8, sad: 0.2}`. Scores are just a weighted average across every level's probability, and the confidence number reflects how spread out those probabilities were. Because it only ever emits one token, output tokens are free. It can't write your email or reason out loud, but it can make the decision about the email.

**If you have an LLM call that outputs one word today, go test it against Jev this week.** Router agents and classifiers are the obvious targets. Rippling tried it with their growth engineering team and got 90% accuracy against a 50% LLM baseline, running 8x faster. It didn't win on every use case for them, but it won on enough that they're re-evaluating. Vaibhav's advice: spend a couple of hours of your team's time, run your existing eval, and see what happens to cost and latency.

**Fast, cheap classification changes what your code looks like.** Vaibhav built a BAML library where every type gets a `.feels()` method backed by Jev. So you can write "while the draft feels full of corporate jargon, keep rewriting" as an actual loop, and the Jev check is so fast it feels invisible next to the LLM call doing the rewrite. He also wrote `grep_with_vibes`, which runs a feeling check on every line of stdin in parallel. Pipe `git log` through it with "this would be scary to revert" and you get back the GC-related commits you really shouldn't touch. None of this is a language feature. It's a blanket interface implemented on top of BAML, so it works on strings, numbers, classes, anything.

**You can turn a coding agent into a state machine, but the action space gets tight fast.** Dex tried using Jev as a tool-calling harness for code search: the state is "files read so far," and each step picks from options like `read_dir apps` or `read_file components/foo.ts`. The catch is Jev picks from a menu and can't generate arguments. You get roughly 255 options and about 32K input tokens, so they capped it at around 80 files per step and had the harness do the deterministic ranking of what to offer next. Dex called it "absolutely an abuse of Jev" with results to match. The same framing is exactly why Jev is great at playing Snake, though. Only four moves, every turn.

**A smaller, faster model still needs a harness around it.** Someone asked what happens if you embed Jev in your code with no fallback. The answer is the same as for any small model: it will be wrong sometimes. For a voice agent, for example, you'd run the fast loop up front and add a watchdog agent that reads the main agent's context and steers it when it goes off track. Faster and cheaper means you need to build for the times it's incorrect.

**If you remember one thing from this session:**

Stop generating text for decisions that only have a handful of valid answers. Routing, classification, "is this urgent," "which team owns this": if the output is picked from a list, a system one model like Jev can make that call faster and cheaper, which means you can afford to make it on every line, every message, every loop iteration. Dex's prediction is that every model provider ships its own version of this. Get the harness and evals right now and you can swap implementations later.

**Next session: GTM Engineering and AI at Rippling, September 29th**

We're breaking down GTM engineering: applying software engineering principles, custom data pipelines, and AI agents to go-to-market ops. John Kutay from Rippling joins us to show how they actually do it in practice. Sign up here: https://luma.com/gtm-engineering

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
