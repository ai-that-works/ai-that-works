# 🦄 ai that works: Software Factories: Hands on with Real Builders

> Dex and Vaibhav sit down with two hands-on software factory builders from the AI unconference: Tyler Brown, who grew a two-person HIPAA-compliant chat startup from $270K to $400K ARR in three months by rebuilding his engineering process around agents, and Cole Murray, maintainer of Open Inspect, an open source background-agent system deployed at companies with up to 500 engineers.

[![Software Factories: Hands on with Real Builders](https://img.youtube.com/vi/HGizPRQfpdw/0.jpg)](https://www.youtube.com/watch?v=HGizPRQfpdw)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-08-hands-on-software-factories)

## Episode Highlights

> "As models get more capable, you actually need a better harness and more checks and balances around it, to make sure that if it goes off for three hours it's not gonna come back with something that you throw away."

> "You can outsource the thinking, but you can't outsource the understanding."

> "Verifiers, in my opinion, are the most important thing now. I sort of consider code review anything that you can't verify, and the goal is to verify as much as possible."

> "I think the orchestrator and the control plane is actually the easiest part of the problem. The actual hard part is what is running in that compute, because that is your dev environment."

> "Don't blame the intern, blame the process error. Patch that process system, and if you can't support it, don't bring interns onto your team."

## Key Takeaways

- **Tyler's team runs a plan, do, verify loop, and the plan phase is the part that's still hard.** He and his co-founder switched from iterative plans to declarative ones: describe the end state and let the agent figure out how to get there. Every week they turn postmortems from failed runs into GitHub issues and use them to upgrade the harness itself, so the bottleneck has moved from code review to planning.
- **An "orchestrator chat" lets one person run six PRs at once without losing the thread.** Tyler pastes a day's worth of feature ideas, pulled from customer demo notes, into a single chat that manages multiple agent sessions underneath it. When a customer reports a bug, the agent creates sub-tickets in `Linear`, pulls context from `Sentry` and `PostHog`, and comes back with root-caused fixes for review, "Tinder style, swipe left, swipe right."
- **The orchestrator is the easy part; the dev environment is the hard part.** Cole has deployed Open Inspect at companies with up to 500 engineers, and his read is that spinning up an agent session from a Slack message or web request is a solved problem. The real difficulty is what's running inside the compute, especially once a company has hundreds of internal repos and services the agent needs to understand.
- **When an agent can't clear login, you build a bypass instead of handing out credentials.** A contractor blocked on OAuth at 3am mocked out the entire login provider so the agent could run and test without real credentials. It's the same instinct behind Cole's dev-environment fixes: re-architect the app to need as few upstream dependencies as possible so the factory can actually run it.
- **PM-authored bug fixes work, but only if you scope them like you'd scope a new hire.** Start non-technical folks on small, contained bugs, let them create the actual PR, and expect the first attempts to be rough. As trust builds, scope grows. Don't let the intern near a database migration, and if that happens anyway, it's a process error to fix, not the intern's fault.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=HGizPRQfpdw)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
