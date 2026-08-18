Hello {firstName},

This week's 🦄 ai that works session recaps the AI That Works Unconference from this past Saturday, August 8th, a day spent with some of the sharpest people building with AI in one room. This episode is Vaibhav and Dex unpacking what came up: cache engineering, harness design, evals for skills, and the question everyone in the room kept circling back to. How do you keep AI-written code from turning into a mess?

The full recording is on [YouTube](https://www.youtube.com/watch?v=fyZ0i4USjgc), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-08-11-unconference-recap).

**Nobody at the unconference disagreed on one thing: unattended models write slop code.** Every single person there is running a different process, and everyone changes that process every few months. The framing that stuck: "we're all still figuring stuff out." Nobody claimed to have found the setup that lets you skip review forever.

**Some teams built seventy deterministic linters instead of updating a prompt.** One attendee described a Rust codebase where, every time the team catches an anti-pattern, they don't add a note to the agent's memory or skills file. They write a linter for it, so the next time that pattern shows up, the agent gets a hard signal instead of a vibe. Dex's counterpoint: for cheaper, faster models like DeepSeek V4 Flash, a plain list of a hundred "this should never happen" rules gets you almost as far, just slower and pricier per check. If a feature costs a thousand dollars to ship, five dollars for a lint pass on top of it isn't a hard call.

**Evals for skills, not just for output, was the idea that stuck with Vaibhav.** Split a software factory into planning and implementing. The implement loop, given a plan, a skill set, an environment, and tests, turns out to be fairly solvable and evaluable: if the output is bad, it's the skill, the plan, or the environment, and you can isolate which. That means you can take a plan you already know worked, swap out one skill, and rerun it to check whether the implementation still holds up. Planning is still the hard, hard-to-eval part.

**Almost everyone at the unconference had independently converged on some form of adversarial review before a human ever sees the diff.** Different names, same shape: run a loop that pokes holes in the output before it reaches a person, so by the time a human looks at it, the odds of it being right are already stacked in their favor. Dex's caveat: the word "adversarial" doesn't do the work by itself. It catches the dumb stuff faster, but it isn't a magic fix.

**Changing a model's reasoning effort mid-conversation invalidates your entire prompt cache, not just the reasoning block.** Reasoning tokens sit near the front of the prompt, so flipping "low" to "high" partway through blows away everything cached after it, all the way back to the start. One detail that surprised the room: some models that only officially document "medium" and "high" reasoning will still mostly respect "low" if you pass it, because the training data taught them what it means even without an explicit mode for it.

**Where do you put your plan docs? Not in Git.** Dex walked through the progression almost every team seems to hit: check plan.md into the repo, then split it by feature, then lose track of which branch a plan actually lives on, then discover GitHub can't comment on a document unless it's a diff. HumanLayer's fix was to git-ignore the plans entirely and sync them to an external system instead. A hook pushes file changes to an API, a web UI renders them with comments and version history, and a watcher syncs updates back down to the file system so multiple agents editing the same doc stay in sync without Git in the loop.

**If you remember one thing from this session:**

If you're not reading the code, you have no idea how much garbage is in it. That's the line from a tweet Dex pulled up mid-episode, and it summed up the unconference's real consensus: nobody's arguing that AI writes clean code by default. Everyone in that room was just building a different system to catch the mess before it compounds.

**Next session: Syncs and A/B Testing 200 Agents, August 18th**

Two guests join us for a two-part episode. What actually happens when you spin up 200 agents in parallel to run real A/B tests, and how do you cleanly sync data from raw state, through your agent layer, down to the frontend? Sign up here: https://luma.com/syncs-and-ab-testing

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
