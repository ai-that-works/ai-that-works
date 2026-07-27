# 🦄 ai that works: No Vibes Allowed - July Edition

> Live from HumanLayer HQ, Dex brings a half-spec'd feature called "context shards" (a volume-based memory system for coding agents sourced from your whole team) and Vaibhav tears into it. Real design conversation, real trade-offs, real production systems.

[Video](https://www.youtube.com/watch?v=rTn8Vhdt-Jo)

[![No Vibes Allowed - July Edition](https://img.youtube.com/vi/rTn8Vhdt-Jo/0.jpg)](https://www.youtube.com/watch?v=rTn8Vhdt-Jo)

## Episode Highlights

> "Twenty percent of the possible memories, but all really useful and applied at the right time, is way better than everything you might want to remember applied all the time."

> "What I get is a lagging indicator for what my memory is. But what I get in return is my memory is never useless."

> "It's a new inbox. And I don't want a new inbox. Give me the inbox I already use, which is Slack."

> "Anyone that tells you they have a supervisor agent, that's all they have. A couple of prompts that they send to a model that inject more prompts into the main loop."

> "Just burn the frickin' tokens. Then one day you wake up and you're spending too many tokens on that. Great, you found your bottleneck."

> "We just made so many decisions that are going to change the shape of the solution by 20 or 30 percent. How much harder would it be to change that after I had gone and actually built it?"

## Key Takeaways

- **Memory should be a lagging indicator, not a single decision.** Vaibhav once told Claude to add a `BAML_DISABLE_DISK_CACHE` env var. Claude saved it to memory, and now every new feature gets its own env var feature flag that he has to strip out by hand. Context shards flip the trigger: something enters memory because analytics show it being said across many sessions, not because the model decided it once.
- **Sourcing memories from the whole team is the actual unlock.** Dex mocked up personal shards and shared shards; Vaibhav wanted the personal tier deleted. If five people on an eight-person team keep telling the agent the same thing, the sixth should get it too, and the split just creates three slightly different versions of the same rule. One canonical library per team gets you the data eight times faster.
- **Don't build a new inbox.** A review queue of pending memories is just another place to check. Route it to Slack where people already are, so approval is a yes/no from your phone. Dismissing a shard snoozes it for 30 days, and if you're still saying the same thing a month later, it comes back and asks again.
- **A "supervisor agent" is usually just a small prompt with a structured output.** HumanLayer's runs a post-tool-use hook on every write, parses the doc's front matter, and if it's a design discussion, sends the markdown to Haiku with one question: are there open questions left? If yes, the write response gets extra context injected telling the agent to move to the outline phase. Under a second, no agent loop.
- **Budget cost and latency per loop, not per system.** If you'll spend $100 on the main agent loop for a task, you'll spend maybe $10 on the system that makes that loop better. The trigger determines the mode: cron-triggered generation runs overnight in batch where lag is free, a Slack message runs instantly because a human is waiting.
- **Ship an internal admin view before you ship evals.** Look at every generation, mark it good or bad, and turn the bad ones into test cases. Then hand those to a model and have it change the prompt until they all pass. That builds an eval set from real generations instead of guesses made before the feature exists.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=rTn8Vhdt-Jo)
- [GitHub Repo](https://github.com/ai-that-works/ai-that-works/tree/main/2026-07-21-no-vibes-july)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

## Links
