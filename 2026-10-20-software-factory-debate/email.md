Hello {firstName},

This week's 🦄 ai that works session was the Software Factory Debate. Zach, founder and CEO of Warp, joined Vaibhav and Dex to argue about what a software factory is, how you measure one, and why most companies don't have one yet. Spoiler: it turned out to be more violent agreement than debate.

The full recording is on [YouTube](https://www.youtube.com/watch?v=XUEfIxkdT2Q), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-10-20-software-factory-debate).

**A factory is a loop that lives in the cloud, and you should define it in code.** The shape is familiar: an issue comes in, agents triage it, maybe write a spec, implement, review, QA, push through CI/CD, and monitor. What makes it a factory is that the loop runs in the cloud where you can see work flowing through it. Zach's take is to define the whole thing declaratively, like Terraform: which agents, which skills, which MCPs, which models, where they run. Once it's a folder of files, you can branch it to test a new version, and an agent can suggest a diff against it when it spots a pattern of failed runs.

**Don't start with full automation. Start by getting the work into the loop.** Vaibhav's instinct was to strip humans out of your existing process first. Zach goes the other way. Most of what can be fully automated today is pretty simple, so Warp gets teams sending even hand-written prompts through the shared loop, from Slack, Jira, or an MCP. A prompt like "here's a screenshot and a Figma link, fix this user-facing bug" is still a human prompt, but now it's tracked and measurable, and over time you turn the repeat ones into triggers.

**Measure more than PR count.** Warp's default factory metrics are DORA metrics, cost (by engineer and by factory stage), and an automation index that counts how many times a human had to steer each PR, so you can push the number down instead of arguing about "automated or not." Then there are online evals on recorded runs. For example: what percentage of runs wrote redundant tests, according to an LLM judge? Split that by model and "I think Opus writes too many tests" stops being a vibe. Another: catch an agent trying six different commands to run the test suite, and turn that relearning into a skill.

**Your real work is your best benchmark.** If you record the model, the environment, and the starting SHA for every run, any good or bad task can become a replayable benchmark, basically your own SWE-bench built from your own front end tickets. The catch is cheating. The agent can fast forward to the finished commit or see the PR that already landed, so you have to rebuild a clean environment for the replay to mean anything.

**Code review is now risk management.** Vaibhav showed a tool Boundary built on top of an owners file: rules that run on every changed file, from a regex (any new `std::env::var` in the Rust source) to a Jev prompt ("does this change add an S3 dependency?"). When a rule fires, that file gets held until the named human approves it. Dex shared a related story. A founder let PRs under a certain size that didn't touch core modules merge without human review. The share of PRs that qualified jumped from about 10% to 80%, because engineers started splitting the risky parts into their own PRs.

**Plan just enough, then build it twice.** Dex frames planning as expected pain: the chance you'll have to change something times how painful that change is. He never plans a button color with the agent, but he does plan a database table. Spend 20 or 30 minutes cutting out most of that pain and then go build. Vaibhav's trick for hard changes: once it works, have the agent write down what it learned, rewrite the spec as if starting from scratch, delete the code, and implement it again. It costs more tokens and gets him better code.

**If you remember one thing from this session:**

The bottleneck is your org chart, not your agents. Most companies draw a line where product owns what's worth building and engineering owns building it. A factory needs one owner for the whole loop, all the way to the customer outcome, like "this workflow used to take a user twenty minutes and now takes ten." If your VP of Product and VP of Engineering won't co-own that, the factory stays a nicer IDE. Working in the open matters too. When prompts happen in a public Slack channel, everyone gets to see how your most senior engineers steer an agent.

**Next session: Building Evals on Production Data, tomorrow (October 27th) at 10 AM PT**

We've done plenty of deep dives on eval design and eval frameworks. This time it's practical: taking your production data and using it to design and extend your eval system. Sign up here: https://luma.com/evals-on-prod-data

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
