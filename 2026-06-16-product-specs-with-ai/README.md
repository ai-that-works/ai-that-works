# 🦄 ai that works: Product Specs with AI

> Splitting the design phase into separate product and technical stages, so AI can ground product decisions in real codebase research, head off bad implementation choices early, and make spec-writing approachable for less-technical people.

[Video](https://www.youtube.com/watch?v=0LPBw3NO3Jc)

[![Product Specs with AI](https://img.youtube.com/vi/0LPBw3NO3Jc/0.jpg)](https://www.youtube.com/watch?v=0LPBw3NO3Jc)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-06-16-product-specs-with-ai)

## Episode Highlights

> "I will use shitty software that has a CLI over good software that doesn't. I've actually been like this for a decade — if I can put it on a bash script, I will tolerate so much jank if I can script it and automate it."

> "At each stage you have less clarity and more leverage. The design is the 25k foot view, the outline is the 10k foot view, and then you actually see the code."

> "We're basically building the prompt for the next model, the next session, and the next context window. I want the percentage of tokens that are relevant to be mostly about the content, not about the formatting."

> "The earlier you are, do more breadth. The later you are, do more verification. How do you remove the cognitive burden of reviewing stuff later and move it earlier in the pipeline — that's what your prompt should do."

> "If you build dev tools, you don't have to build empathy for people who are different than you. It's cheaper to build things for yourself — which is exactly why dev tools is so competitive."

> "I stopped having a CLAUDE.md in our repo, because stuff just gets out of date. A universal CLAUDE.md skews the program more incorrectly than correctly most of the time."

## Key Takeaways

- **Split the design phase into product design and technical design as two separate steps.** Product design covers user experience, what success looks like, and what is out of scope. Technical design covers architecture, contracts, and a new "program design" step for test seams and function signatures. Without the split, a discussion nails the UX, declares itself done, and the implementation still comes out wrong because nobody aligned on how the program would be laid out. Vaibhav's team treats the spec itself as the artifact, not commits: one recent spec had 112 comments across seven sub-pages before any code was written.
- **Make product specs something a PM can touch by grounding them in codebase research.** Most product questions aren't technical, so the people who care most should be able to participate. HumanLayer's PRD skill generates HTML mockups, streams them to S3, and renders them in an iframe so the team can comment like on a Google Doc. Dex rethought their task page from a flat table of sessions into a deliverables-focused workflow view, generating several mockup options (`group-by-task`, a pipeline stepper, a deliverables gallery) and iterating visually instead of in code.
- **Ask the agent to define how success will be measured, then come back and check it.** During product design, have the agent work out a concrete metric: did the workflow get 10% faster, did conversion go up, are more people using the feature. Because the goal is measurable, you can spin up an agent weeks later to pull the numbers and decide whether the problem is solved. The nuance is knowing when the lever applies, Dex skipped metrics in the live demo because it was a pure exploratory UI change.
- **Move decisions and verification as early in the pipeline as possible, where you have the most leverage.** The "program design" step exists because designs looked great and code still came out wrong: the model kept reaching for a React provider with `useEffect` and context, patterns HumanLayer avoids because they use `Zustand` and `TanStack` collections. Now the model asks up front, "provider or `TanStack` collection?", catching the bad decision before the PR exists. Vaibhav reads a standardized PR step reporting what deviated from the plan every time, because that diff is where the bugs hide.
- **Pick your artifact format by audience: Markdown for models, HTML for humans.** A research doc that mostly feeds the next model should be Markdown, because it is far more token-efficient and keeps relevant tokens on content, not formatting. HTML is for humans, where the raw file is ugly but the rendered artifact is great (Vaibhav often converts HTML to SVG or PNG before feeding it to a model). They debated `MDX` and skipped it: it blends Markdown and React nicely but isn't standardized, breaks on GitHub, and needs a React runtime, while plain Markdown and rendered HTML work everywhere.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=0LPBw3NO3Jc)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
