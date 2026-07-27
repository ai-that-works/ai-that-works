Hello {firstName},

This week's 🦄 ai that works session was No Vibes Allowed, live from HumanLayer HQ in San Francisco. Dex brought a half-spec'd feature called context shards, Vaibhav tore into it for an hour, and the design came out meaningfully different than it went in. No slides. Just the actual conversation two teams have before anyone writes code.

The full recording is on [YouTube](https://www.youtube.com/watch?v=rTn8Vhdt-Jo), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-07-21-no-vibes-july).

**Memory should be a lagging indicator, not a single decision.** Here is why Claude's memory feature fails in practice. Vaibhav once told Claude to add a `BAML_DISABLE_DISK_CACHE` env var. Claude saved that to memory, and now every new feature it touches gets its own env var feature flag whether he wants one or not. He has to strip them out by hand every time. Context shards flip the trigger: nothing enters memory because the model decided it once, only because analytics show the same thing being said across many sessions. You get maybe 20% of the memories you could have captured, but they are all correct. Vaibhav's framing was that 20% useful memory applied at the right time beats everything you might want to remember applied all the time.

**Sourcing memories from your whole team is the actual unlock.** Dex's mocks had personal shards and shared shards. Vaibhav wanted the personal tier deleted entirely. His argument: if five people on an eight-person team keep telling the agent the same thing, the sixth person should get it too, and the split just creates three slightly different versions of the same rule that someone has to reconcile. One canonical library per team. The reason it works is throughput. One engineer generates memory candidates at one engineer's pace. Eight engineers get you there eight times faster, and your `CLAUDE.md` stays current without anyone owning the chore.

**Do not build a new inbox. Ship into the one people already check.** Dex had a review queue UI mocked up. Vaibhav's reaction was that a queue of pending memories is just another inbox, and he already has too many. Send it to Slack, where he can hit yes or no from his phone between prompts. The dismiss behavior matters just as much: dismissing a shard snoozes it for 30 days, and if you are still telling the agent the same thing a month later, it comes back and asks again. Fire and forget, then remind me later if it is still true.

**A "supervisor agent" is usually just a small prompt with a structured output.** Here is exactly what HumanLayer runs today. A post-tool-use hook fires on every write and calls their API. The API parses the doc's front matter, and if the type is a design discussion, it sends the 200-line markdown file to Haiku with one question: are there open questions left? If yes, the response to the write call gets extra context injected saying all design decisions are resolved, remind the user to move to the outline phase. The whole thing returns in under a second. No agent loop, no tool catalog, no swarm. Fifteen little pipelines like that keep a long session on track without the user needing to know the workflow.

**Budget cost and latency per loop, not per system.** Vaibhav's rule of thumb from the whiteboard: if he is willing to spend $100 on the main agent loop for a task, he is willing to spend around $10 on the system that makes that loop better. Same model is fine, but the execution mode should follow the trigger. Cron-triggered generation runs overnight in batch mode where lag costs nothing. A Slack message from a user runs instantly, because a human is standing there. Write down what triggers each loop before you write the prompt, because the trigger determines the whole cost profile.

**Ship an internal admin view before you ship evals.** Rather than spend a month building an eval set for the shard generator, Dex is building a view where he can look at every generation and mark it good or bad. The bad ones become test cases, then you hand those to a model and tell it to change the prompt until they all pass. That is how you build an eval set: from real generations you have actually looked at, not from guesses made before the feature exists. Vaibhav's version of this is "burn the tokens." Run it expensively until you find the bottleneck, then decide whether it is worth engineering. If it was never valuable, you turn it off and you are out a few dollars instead of a month.

**If you remember one thing from this session:**

The reason this design conversation worked is that Dex showed up having already thought through every user interaction, with mockups grounded in Vaibhav's actual codebase. Not a wireframe. Clickable HTML with the canary branch example baked in. That meant Vaibhav could skip past clarifying questions and go straight to arguing about the shape of the solution. Twenty minutes of that changed the feature by 30%, before it was 20,000 lines of code that would need rewriting. One person deep-thinks it, one or two people read the doc and then argue about it, the original person drives it home.

**Tomorrow's session: Your Model is Already Obsolete, July 28th**

Opus 5, Sonnet 5, Grok 4.5, Kimi K3, GPT-5.6, Gemini 3.6, all in the last month. Any one of them could make your agent smarter or your bill smaller. Meanwhile every model you have in production just got a month closer to its retirement date. Model deprecation is one of the only outages you get advance notice of, and teams still treat it like a surprise. We are showing you how to make a model swap a non-event. Sign up here: https://luma.com/easy-model-swaps

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
