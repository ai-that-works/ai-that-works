# 🦄 ai that works: GTM Engineering and AI at Rippling

> In this episode, we break down GTM Engineering, the practice of applying software engineering principles, custom data pipelines, and AI agents to go-to-market ops. We will be joined by John Kutay at Rippling to see how they do this in practice

[Video](https://www.youtube.com/watch?v=bGMiRmXbRUs)

[![How Rippling Replaced BI Dashboards with AI Agents (GTM Engineering)](https://img.youtube.com/vi/bGMiRmXbRUs/0.jpg)](https://www.youtube.com/watch?v=bGMiRmXbRUs)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-29-gtm-engineering)

## Episode Highlights

> "The first-class citizen of analytics is chatting with data, and not only chatting with data but taking action and using data in the path of your operation."

> "LLMs don't always generate good, efficient queries. After we released this, we had to do a lot of work to actually do some SQL validation."

> "Hallucination has gone away. There's slightly inaccurate output, or not the intended output, but it's not the LLM coming up with total garbage from nowhere."

## Key Takeaways

- **A dashboard nobody acts on is wasted work.** Someone has to find the report, interpret it, and agree it's the source of truth, and adding one more column can mean plumbing it through a pile of data models. At Rippling the interface is now chatting with the data in the path of the work: a marketer says "tell me what's working" and the agent pulls past email performance by job title and drafts copy recommendations.
- **Start with retrieval as a tool, then graduate to text-to-SQL.** Phase one was deterministic: a human or coding agent wrote the SQL, code ran it, and a `get_leads` tool mapped to one specific query. Phase two let the agent write its own SQL, which kicks off a reasoning loop of roughly 5 to 20 queries per question, ending with the agent asking itself "did this answer the question?"
- **Agent-written queries will hurt your warehouse, so plan for it.** Rippling added SQL validation with SQLGlot, an open source parser that checks the query before it runs. They then watched which queries the agent kept running and built pre-aggregated tables for the common ones, with skills and tools so the agent knows to use them. Whether a rollup is worth building depends on whether a question is a one-off or about to become standard practice, so that step stayed human in the loop.
- **Test decision models like Jev on your real workloads, and expect a split.** As the "did we answer the question?" check inside the text-to-SQL loop, Jev was faster but the answers got worse and it tanked their evals. For classifying messy, free-form data into structured categories, it worked well, was much faster, and is cheaper, so it went into their internal agent harness.
- **Evals are in CI, and Slack complaints are your other eval.** Rippling doesn't change a major agent without running evals first, but John put real decision-making closer to 50/50 between benchmarks and user feedback. When the eval says great and the feedback channel fills up with "this isn't working," they treat it as a bug in the benchmark and fix the benchmark.
- **Own the system end to end with a coding agent at the center.** Rippling is building toward a "GTM super app," one internal app that one team owns and keeps improving, instead of a stack of Martech tools and a slow BI queue. They already have a pipeline that triages user asks and opens the PR, and what's left to guard against is slightly-off output rather than hallucination.


## Resources

- [Session Recording](https://www.youtube.com/watch?v=bGMiRmXbRUs)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

