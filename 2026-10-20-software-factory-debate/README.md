# 🦄 ai that works: Software Factory Debate

> Zach is the founder and CEO of Warp, and he has a lot to say on software factories and how to get the most out of agentic coding. Dex and Zach agree on some things, and it seems like they might disagree on one or two. Whiteboard-backed debate format moderated by Vaibhav.

[Video](https://www.youtube.com/watch?v=XUEfIxkdT2Q)

[![How to Build an AI Software Factory That Ships Faster](https://img.youtube.com/vi/XUEfIxkdT2Q/0.jpg)](https://www.youtube.com/watch?v=XUEfIxkdT2Q)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-10-20-software-factory-debate)

## Episode Highlights

> "As a developer, your job is not just going to be building products anymore, it's going to be building, maintaining, and tuning this loop to make software production as good as possible."

> "Code review is becoming an exercise in risk management."

> "Fundamentally, you cannot have a factory if you have two separate orgs that have to own both of it."

## Key Takeaways

- **A software factory is a loop that lives in the cloud, defined in code.** Issues come in at the top and agents triage, spec, implement, review, QA, ship, and monitor. Zach's approach is to define the agents, skills, MCPs, and models declaratively, like Terraform, so you can branch the factory to test a new version and let an agent propose a diff against it when it spots a pattern of failed runs.
- **Start by routing work through the loop, not by automating everything.** Fully automatable work is still pretty simple today, so Warp gets teams sending even hand-written prompts (a screenshot and a Figma link from Slack, a Jira ticket, an MCP call) through the shared loop. Once it's tracked and measurable, the repeat ones become triggers.
- **Measure more than PR count.** Track DORA metrics, cost by engineer and by stage, and an automation index that counts how often a human steered each PR. Add online evals on recorded runs, like "what percentage of runs wrote redundant tests?" split by model, or catching an agent trying six commands to run the tests and turning that into a skill.
- **Recorded runs become your own benchmark.** With the model, environment, and starting SHA saved, any real task can be replayed against a new model or skill version. The catch is cheating: you need a clean environment so the agent can't fast forward to the finished commit or see the PR that already landed.
- **Code review is now risk management.** Boundary runs rules on every changed file, from a regex for a new `std::env::var` to a Jev prompt asking "does this add an S3 dependency?", and holds that file for a named human. One founder let small PRs that skip core modules merge without human review, and the share that qualified jumped from about 10% to 80% as engineers split out the risky parts.
- **The bottleneck is the org chart.** When product owns what to build and engineering owns building it, nobody owns the whole loop through to the customer outcome. A factory needs those two co-owning it, plus a culture of working in the open where everyone can see how senior engineers prompt.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=XUEfIxkdT2Q)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
