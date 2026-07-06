Hello {firstName},

This week's 🦄 ai that works session was on product specs with AI. The core idea: most planning processes quietly tangle two very different decisions together. Product decisions like "how should this feel" get mixed with technical decisions like "which state library do we use," and the important questions on both sides get missed.

The full recording is on [YouTube](https://www.youtube.com/watch?v=0LPBw3NO3Jc), and the notes are on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-06-16-product-specs-with-ai).

**Split the design phase into product design and technical design as two separate steps.** Dex's team evolved their research-plan-implement flow by breaking design in two: product design covers the user experience, what success looks like, and what is out of scope. Technical design covers architecture, contracts, and a new "program design" step for test seams and function signatures. Here is why the split matters. A single combined design discussion would nail the user experience, declare itself done, and then the actual implementation would come out wrong because nobody ever aligned on how the program would be laid out. Vaibhav runs a parallel version where someone spends two or three days iterating with the model and the artifact is a design spec, not commits. One of his recent specs had 112 comments across seven sub-pages before a line of code got written.

**Make product specs something a PM can actually touch by grounding them in real codebase research.** Most product questions are not technical, so the people who care most about them should be able to participate. HumanLayer's PRD skill generates HTML mockups, streams them to S3, and renders them in an iframe so the whole team can comment on the artifact like a Google Doc. Dex walked through a live ticket: rethinking their task page from a flat table of sessions into a workflow view organized around the actual deliverables. He generated several mockup options (group-by-task, a pipeline stepper, a deliverables gallery) and iterated on them visually instead of in code. It will not replace Figma, but it does the cheap early product work that usually never gets done.

**Ask the agent to define how you will measure success, then come back and check it.** During product design, Dex has the agent work out a concrete success metric: did this workflow get 10% faster, did conversion go up, are more people using the feature. The payoff comes later. Because the goal is measurable, you can spin up an agent weeks afterward to go pull the numbers and tell you whether the problem is actually solved. The nuance: in his live demo he deliberately skipped metrics because it was a pure exploratory UI change, so knowing when the lever applies and when to wire it in later is part of the skill.

**Push decisions and verification as early in the pipeline as you can, because that is where you have the most leverage.** The whole reason the program design step exists is that designs looked great and the code still came out wrong. The concrete failure: during implementation the model would reach for a React provider with a useEffect and context, patterns HumanLayer specifically avoids because they use Zustand and TanStack collections. So now the model asks up front, "do you want a provider or a TanStack collection?" and the bad decision gets caught before the PR exists. Vaibhav's favorite related habit is a standardized PR step that reports exactly what deviated from the plan. He reads that diff every single time because that is where the bugs hide, and it replaces a full code read.

**Pick your artifact format by who is reading it: Markdown for models, HTML for humans.** A research doc that mostly feeds the next model should be Markdown, because it is far more token-efficient and keeps the relevant tokens focused on content instead of formatting. HTML is for humans, where the raw file is ugly but the rendered artifact is great. Vaibhav often converts HTML to SVG or PNG before handing it to a model, since raw HTML is one of the least information-dense formats you can feed an LLM. They debated MDX and landed on skipping it: it blends Markdown and React nicely, but it is not standardized enough, breaks on GitHub, and needs a React runtime, while plain Markdown and rendered HTML work everywhere.

**If you remember one thing from this session:**

Separate product design from technical design, and move every decision you can to the earliest point in the pipeline. The earlier you are, the more breadth and leverage you have and the less it costs to change your mind. The later you are, the more it is about verification. A good spec process front-loads the decisions so review at the end is cheap, and it lets the less-technical people on your team shape the product without getting lost in the patterns debate.

**Next session: Software Factory for Agent Tools, June 23rd**

Everyone is obsessed with software factories, and the heart of a software factory is a persistent feedback loop. Vaibhav and Dhilan will show a loop they built to test new BAML language features 24/7, improving the language based on feedback from coding agents that are trying to implement features against it. Sign up here: https://luma.com/agent-tools-software-factory

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
