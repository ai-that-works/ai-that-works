# 🦄 ai that works

> ​a weekly conversation about how we can all get the most juice out of todays models with [@hellovai](https://www.github.com/hellovai) & [@dexhorthy](https://www.github.com/dexhorthy)

### 📅 event calendar - https://lu.ma/baml

every tuesday at 10 am pst on zoom.

1 hour of live code, q&a with some prepped content to help you take your ai app from a demo to production.

lets code together 🧑‍💻

## pre-reading
​to prevent repeating the basics, we recommend you come in having already understanding some of the tooling we will be using:

* zoom 
* ​cursor (a vscode alternative)
* ​programming languages
    * ​application logic: python or typescript or go (depends on session)
    * ​prompting: baml
        * repo: [github.com/boundaryml/baml](https://github.com/boundaryml/baml) 
        * recommend [getting started video](https://gloochat.notion.site/benefits-of-baml)
    * package managers of choice:
        * Python - [UV](https://docs.astral.sh/uv/getting-started/installation)
        * Typescript - PNPM

## sessions

| topic | description |
| ----- | --------- |
| 2025-06-10<br/>**Cracking the Prompting Interview**<br/>[youtube](https://youtu.be/PU2h0V-pANQ) • code • [RSVP](https://lu.ma/5bv91n0a) | ​Ready to level up your prompting skills? Join us for a deep dive into advanced prompting techniques that separate good prompt engineers from great ones. We'll cover systematic prompt design, testing tools / inner loops, and tackle real-world prompting challenges. Perfect prep for becoming a more effective AI engineer. |
| 2025-06-03<br/>**Humans as Tools: Async Agents and Durable Execution**<br/>[youtube](https://youtu.be/NMhH5_ju3-I) • [code](./2025-06-03-humans-as-tools-async) • PAST | ​Agents are great, but for the most accuracy-sensitive scenarios, we some times want a human in the loop. Today we'll discuss techniques for how to make this possible. We'll dive deep into concepts from [our 4/22 session on 12-factor agents](./2025-04-22-twelve-factor-agents) and extend them to handle asynchronous operations where agents need to contact humans for help, feedback, or approvals across a variety of channels. |
| 2025-05-27<br/>**12-factor agents: selecting from thousands of MCP tools**<br/>[youtube](https://www.youtube.com/watch?v=P5wRLKF4bt8) • [code](./2025-05-27-mcp-with-10000-tools) • PAST | MCP is only as great as your ability to pick the right tools. We'll dive into showing how to leverage MCP servers and accurately use the right ones when only a few have actually relevant tools. |
| 2025-05-20<br/>**Policy to Prompt: Evaluating w/ the Enron Emails Dataset**<br/>[youtube](https://www.youtube.com/watch?v=gkekVC67iVs) • [code](./2025-05-20-policies-to-prompts) • PAST | one of the most common problems in AI engineering is looking at a set of policies / rules and evaluating evidence to determine if the rules were followed. In this session we'll explore turning policies into prompts and pipelines to evaluate which emails in the massive [enron email dataset](https://www.cs.cmu.edu/~enron/) violated SEC and Sarbanes-Oxley regulations.  | 
| 2025-05-13<br/>**evals evals evals**<br/>[youtube](https://youtu.be/-N6MajRfqYw) • [code](./2025-05-13-designing-evals) • [RSVP](https://lu.ma/j5y6bd3i) | stay tuned for our season 2 kickoff topic on minimalist and high-performance testing/evals for LLM applications | 
| **Break**  |  We had a great time doing the first four episodes of AI that Works - we'll see y'all may 13th for season 2! |
| 2025-04-22<br/>**twelve factor agents**<br/>[Youtube](https://youtu.be/yxJDyQ8v6P0) • [code](./2025-04-22-twelve-factor-agents) • PAST | learn how to build production-ready AI agents using the twelve-factor methodology. we'll cover the core concepts and build a real agent from scratch. | 
| 2025-04-15<br/>**code generation with small models**<br/>[Youtube](https://youtu.be/KJkvYdGEnAY) • [code](./2025-04-15-code-generation-with-small-models) • PAST | large models can do a lot, but so can small models. we'll discuss techniques for how to leverge extremely small models for generating diffs and making changes in complete codebases. | 
| 2025-04-08<br/>**reasoning models vs reasoning prompts**<br/>[youtube](https://youtu.be/D-pcKduKdYM) • [code](./2025-04-07-reasoning-models-vs-prompts) • PAST | models can reason but you can also reason within a prompt. which technique wins out when and why? we'll find out by adding reasoning to a chat bot that generates complex cypher/sql queries. | 
| 2025-03-31<br/>**large scale classification**<br/>[youtube](https://youtu.be/6B7MzraQMZk) • [code](./2025-03-31-large-scale-classification) • PAST | ​llms are great at classification from 5, 10, maybe even 50 categories. but how do we deal with situations when we have over 1000? perhaps its an ever changing list of categories? | 
