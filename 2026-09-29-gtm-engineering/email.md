Hello {firstName},

This week's 🦄 ai that works session was a look inside how Rippling does GTM engineering. John Kutay, who runs growth GTM AI engineering there, joined Vaibhav and Dex to walk through how they went from BI dashboards to an internal agent that answers sales and marketing questions and acts on the answers.

The full recording is on [YouTube](https://www.youtube.com/watch?v=bGMiRmXbRUs), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-29-gtm-engineering).

**A dashboard nobody acts on is wasted work.** John's point: the report exists, but someone has to find it, interpret it, and agree it's the source of truth. And if you want one more column, you're plumbing it through a pile of data models. At Rippling the first-class interface is now chatting with the data and using it in the path of the work. A marketer can say "I'm putting together a new campaign, tell me what's working" and the agent pulls past email performance by job title and drafts copy recommendations from it.

**Start with retrieval as a tool, then graduate to text-to-SQL.** Phase one was boring on purpose. A human (or a coding agent) wrote the SQL, deterministic code ran it, and the results went into the agent's context. A `get_leads` tool mapped to one specific query. Phase two let the agent write its own SQL, and that's where it got interesting. A single question kicks off a reasoning loop of roughly 5 to 20 queries, with the agent asking itself "did this actually answer the question?" at the end.

**Agent-written queries will hurt your warehouse, so plan for it.** A BI dashboard is efficient because an analyst built it once and the caching works. An agent exploring a question runs a lot of queries nobody has tuned. Rippling added SQL validation using SQLGlot, an open source parser that checks the query itself before it runs. Then they watched which queries the agent kept running and built pre-aggregated tables for the common ones, with tools and skills so the agent knows to use them. That last part stayed human in the loop. Whether a rollup is worth building depends on whether this question is a one-off or about to become standard practice, and that context lives in your team's heads.

**Test decision models like Jev on your real workloads, and expect a split.** John ran Jev on two things. As the "did we answer the question?" check inside the text-to-SQL loop, it was faster but the answers got worse and it tanked their evals. He allows it might be his implementation. For classification of messy, free-form data into structured categories, it worked well, was much faster, and is cheaper, so they built it into their internal agent harness. His approach to Jev, or OpenAI's new decision API, or whatever ships next: run it against your internal benchmark and see what actually works.

**Evals are in CI, and Slack complaints are your other eval.** Rippling doesn't change a major agent without running evals first. But John says real decision-making is closer to 50/50 between benchmarks and user feedback. They collect thumbs up and thumbs down, and when the eval says great but the feedback channel fills up with "this isn't working," they treat it as a bug in the benchmark and go fix the benchmark.

**If you remember one thing from this session:**

Own the system end to end, and put a coding agent at the center of it. John's team is building toward a "GTM super app," one internal app that one team owns and keeps improving, instead of a stack of Martech tools and a slow BI queue. They already have a pipeline that triages user asks and opens the PR. Hallucination, he said, basically never comes up anymore. What you still get is output that's slightly off, which is why the guardrails and evals matter more than the model choice.

**Next session: Building a Memory Pipeline, October 6th**

We've talked about memory supervisors and memory pipelines before. This time we're getting into real code with real problems and real constraints. Sign up here: https://luma.com/memory-pipeline

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
