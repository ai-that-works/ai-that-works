Hello {firstName},

This week's 🦄 ai that works session brought two hands-on software factory builders onto the show: Tyler Brown, who grew a two-person HIPAA-compliant chat startup from $270K to $400K ARR in three months by rebuilding his engineering process around agents, and Cole Murray, maintainer of Open Inspect, an open source background-agent system deployed at companies with up to 500 engineers.

The full recording is on [YouTube](https://www.youtube.com/watch?v=HGizPRQfpdw), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-08-hands-on-software-factories).

**Tyler's team runs a plan, do, verify loop, and the plan phase is the part that's still hard.** He and his co-founder switched from writing iterative plans to declarative ones: instead of spelling out every step, they describe the end state and let the agent figure out how to get there. The "do" phase is nearly automated. If it goes well, they merge it. If something's off, they write a postmortem, turn it into a GitHub issue, and every week they use that pile of postmortems to upgrade the harness itself. Bottleneck moved from code review to planning, so that's where they spend their attention now.

**An "orchestrator chat" lets one person run six PRs at once without losing the thread.** Tyler pastes a day's worth of feature ideas, most pulled straight from customer demo notes in Notion, into a single chat with an agent that manages multiple sessions underneath it. When a customer reported a bug, he dropped the support transcript in and the agent created four sub-tickets in Linear, assigned agents to each, pulled context from Sentry and PostHog, and came back with root-caused fixes. His words for reviewing the output: "Tinder style, swipe left, swipe right."

**Cole's read after deploying Open Inspect at companies up to 500 engineers: the orchestrator is the easy part.** Taking in a Slack message or a web request and spinning up an agent session is a solved problem with standard primitives. The actual hard part is what's running inside the compute, your dev environment, especially once a company has hundreds of internal repos and services. Some teams solve it by pre-cloning every repo onto a base image every hour so sessions boot fast. Others discover their agent can't even log in, because the app uses OAuth and there's no way to script past a Google login screen.

**When an agent can't clear login, you build a bypass instead of handing out credentials.** Dex described a contractor blocked on the same problem at 3am: rather than wait for an auth key, he mocked out the entire login provider in the app so the agent could run and test without ever needing real credentials. That's the same instinct as Cole's dev-environment fixes, re-architect the app to need as few upstream dependencies as possible, so the factory (and the agent) can actually run it.

**PM-authored bug fixes work, but only if you scope them like you'd scope a new hire.** Cole's advice: start non-technical folks on genuinely small bugs, like a modal that won't close, let them create the actual PR, and expect the code to be rough at first. As trust builds, the scope grows. Vaibhav's framing: this is exactly how you onboard an intern, except this intern never learns to code, so the guardrails have to do the learning instead. Don't let the intern near a database migration. If you did let that happen, that's not the intern's mistake, that's a process error, and you fix the process.

**If you remember one thing from this session:**

The orchestrator and the control plane are the easy 20%. The dev environment, getting an agent a fast, reproducible place to build and verify changes without babysitting logins and internal dependencies, is where the real engineering time goes. Before you build another Slack bot or ticket router, ask whether your agents can actually run your app end to end without a human unblocking them.

**Next session: Performance Engineering, September 15th**

When milliseconds are too slow, you have to engineer for nanoseconds. We're unpacking N5-level optimization for AI workloads: the techniques for stripping away overhead, optimizing memory throughput, and pushing inference infrastructure to the hardware's absolute limits. Sign up here: https://luma.com/n5-optimization

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
