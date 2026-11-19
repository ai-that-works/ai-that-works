# 🦄 ai that works: Using AI for Writing

> Vaibhav and Aaron (co-founder of Boundary) share how they use AI for writing without producing slop: which models they pick, how they prepped a conference talk by going wide before going deep, and how the BAML team keeps AI-written engineering docs honest.

[Video](https://www.youtube.com/watch?v=V5X34C9qvX4)

[![The Right Way to Use AI for Writing, Presentations, and Engineering Docs](https://img.youtube.com/vi/V5X34C9qvX4/0.jpg)](https://www.youtube.com/watch?v=V5X34C9qvX4)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-11-10-using-ai-for-writing)

## Episode Highlights

> "If all you've given the AI is one idea, it will do what you say and follow that one idea."

> "It's very hard to have AI-isms in your slides if you just have less words."

> "The author of the BEP is given more convenience than the readers of the BEP."

> "We don't want teams of Claude talking to Claude. We want humans talking to humans, but by leveraging the tools that are out there today."

> "If it's good writing, it conveys the idea really well, and it makes your brain think it the way you want, who created it doesn't matter."

## Key Takeaways

- **Pick the model for how you like to read, and give it a style guide.** Aaron writes with Opus 5.5 on medium or high because Astra and Sol read like a scientific paper to him. Vaibhav prefers Sol for facts-and-bullets output and speed. Both point the model at Google's developer documentation style guide, and Vaibhav downloaded all of it while writing the BAML docs.
- **Go wide before you go deep.** Aaron's talk prep started as a scratchpad of screenshots and loose ideas: SpaceX's cost cuts, how Sentry captures traces, a startup that raised $35 million in 2002 to automate unit testing. Hand an AI one idea and it follows that one idea. Seed the context with everything and it surfaces connections, like profiling to densely trace only the rare arms of a `match` statement.
- **Keep the human judgment call.** They dropped the "Raptor 3 of software" angle because neither could name the equivalent of going to Mars for software, even though the model would have invented one. Write an outline where every section answers a question from the title, then read just the titles in order to check the story holds.
- **Fewer words on slides means fewer AI-isms.** Vaibhav tells the AI to delete every word it can, since a five-word slide has nowhere to hide a Claudism. He built the deck in plain HTML and JavaScript, abandoned his first worktree when it went sideways, and says existing slide tools can't match that iteration speed.
- **Make humans the readers of AI-written docs.** BAML enhancement proposals (BEPs) can be fully AI-written, but the comment system only has a human UI. Authors can reply to comments but not create them, so a sloppy author loses BEP privileges and gets read last. Aaron writes every doc as an end-user doc for an entry-level engineer: how will I use this, not how is it built.
- **Good writing is judged by the reader's care, not by who typed it.** Vaibhav compares it to code: if it's good, who created it doesn't matter. Aaron's counterpoint is that readers start skimming the moment they smell AI, so before sending a doc, read it yourself and fix the paragraph you would skip.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=V5X34C9qvX4)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

