Hello {firstName},

This week's 🦄 ai that works session was Dex and Vaibhav zooming in on one specific slice of the software factory: the part where agents actually build and test the thing. They mapped out the four layers every team ends up building or buying, and used Boundary's actual internal stack (agent tries BAML) as the running example.

The full recording is on [YouTube](https://www.youtube.com/watch?v=tGbjIvvYuHE), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-08-25-software-factory-design-patterns).

**Every agentic software factory breaks down into four layers: compute, dev environment, harness, and orchestration.** Compute is just where the agent runs, Boundary uses a pool of MacBooks because they had spare ones lying around and pre-installed tool chains mean zero boot-up time. Dev environment is what the agent needs to actually build and test (language runtimes, access to other services). Harness is Claude Code, Codex, or something custom. Orchestration is the control plane that dispatches work, watches sessions, and decides what to do with feedback. Once you see the four layers, you can decide which ones to own and which ones to buy instead of treating "software factory" as one giant black box.

**The dev environment layer is where teams hit the most friction, and Google and Facebook already solved it a decade ago.** Vaibhav pointed out that at Google, nobody codes on their laptop. You spin up a "cloudtop," every internal web service gets a shareable subdomain by default, and switching machines takes seconds. Most teams building agent factories today are quietly reinventing that same golden path. If your dev environment can't give an agent (or a person) a disposable, reproducible place to build and a URL to share the result, that's the layer to fix first, before you touch harness or orchestration.

**Decide if your dev environment is "pets" or "cattle," because most teams default to pets without meaning to.** A pet is a server you keep alive and patch when it breaks, like Vaibhav's MacBook fleet, where adding a new machine means running a setup script by hand. Cattle is disposable and provisioned on demand, like a PR preview environment that gets a random hash and nobody logs in to fix it if it dies. Dex's take: cattle is the right end state, but pets are a completely reasonable place to start if you're not running thousands of workflows a day. Know which one you're building before you're three months into an architecture that doesn't match your actual load.

**The harness layer has no standard interface yet, and that's not an accident.** Protocols like ACP and AG-UI exist for a harness to talk to a UI, but neither supports hooks, the lifecycle events a control plane needs to react to what an agent is doing mid-session. Claude Code, Codex, and Pi all implement hooks completely differently, because every harness makes different tradeoffs (Claude Code is opinionated and "just works," Pi hands you more control but makes you configure everything). If you're building on top of multiple harnesses, budget real engineering time for that translation layer. Nobody has solved it for you yet.

**Stop forcing a choice between "buy the whole stack" or "build the whole stack."** Dex's framing: it should be composition over inheritance. If you want orchestration that can ping agents from Slack, you shouldn't have to either build your own compute and harness from scratch, or hand a vendor your entire workflow just to get that one piece. Boundary is a concrete example of this in practice: they deliberately don't want to own the harness layer, because harnesses change constantly and they'd rather stay swappable between Claude Code and Codex. Figure out which layer is actually your hard problem, then buy or open-source your way out of the rest.

**If you remember one thing from this session:**

A factory that can't trace a part back to the station that made it can't compute yield, and yield is the entire reason to build a factory in the first place. That's true whether the "part" is a physical widget or a pull request. If you can't tell which layer of your stack produced a bad output, you can't fix it, you can only throw more tokens at the whole pipeline and hope.

**Next session: Code Mode for Extensible Software, September 1st**

Vaibhav is back with a deep dive on why code, not config menus or plugin APIs, is turning out to be the most flexible interface for making software extensible. Think VS Code extensions or iPhone apps, but for the next generation of customizable, agent-built tools. Sign up here: https://luma.com/code-mode-extensible-software

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
