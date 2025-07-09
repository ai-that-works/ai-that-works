# 🦄 ai that works: Context Engineering and memory deep dive

> A deep dive into building effective memory systems for AI agents, focusing on context engineering, scalable memory architectures, and practical implementation patterns.

[Video](https://www.youtube.com/watch?v=-doV02eh8XI) (1h27m)

[![Context Engineering and Memory Deep Dive](https://img.youtube.com/vi/-doV02eh8XI/0.jpg)](https://www.youtube.com/watch?v=-doV02eh8XI)

Links:

- [12 factor agents: Context Engineering](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-03-own-your-context-window.md)
- Bryan's Blog Post on triggers and memory - [Building Proactive AI Agents](https://bryanhoulton1.substack.com/p/building-proactive-ai-agents)
- Previous Episode with deeper dive on structured outputs as context eng: [Cracking the Prompting Interview](https://github.com/hellovai/ai-that-works/tree/main/2025-06-10-cracking-the-prompting-interview)
- [OWL Ontology Time relationships](https://www.w3.org/TR/owl-time/)

## Episode Highlights

> "Treat RAG, memory, and prompts as a single, unified context engineering problem. Think about how to best assemble all necessary information into the final set of tokens for the model."


> "Don't try to make your agent remember everything. Implement a summarization strategy like Decaying Resolution Memory (DRM) to create a focused, scalable memory that surfaces what's important over time."

> "Give your agent semantically meaningful, human-like tools (e.g., 'check_calendar', 'search_inbox') instead of a generic 'retrieve_memory' function. Sandbox these tools to the current user to improve security and simplify the agent's task."

> "Before writing code, clearly define your success criteria and the specific user experience you want to create. Your memory architecture should be a direct solution to that well-defined problem."

> "When creating summarization tasks, provide the model with the existing memory context. This allows it to understand what is 'notable' in the new information relative to the entire history."

> "For tasks where you know the agent will always need certain information (e.g., today's date, user profile), fetch it deterministically and inject it into the context yourself. Don't rely on the agent to ask for it every time."

> "Avoid solving complex, deterministic problems like timezone conversions inside a prompt. Handle that logic in your application code and provide the model with a normalized, simple format to work with."


## Key Takeaways

- "Context Engineering" is the unifying paradigm for building with LLMs. All inputs—prompts, RAG, memory, agent history—are simply different ways of assembling the tokens that go into the model. The quality of your output is a direct function of the quality of this input context.
- Effective memory is not about remembering everything. It's an engineered, lossy process designed to retain the most relevant information for a specific use case. Techniques like Decaying Resolution Memory (DRM) manage this by summarizing information over time, making memory scalable and focused.
- Offload memory and state to sandboxed, stateful tools. Instead of stuffing all data into the prompt, give the agent tools that mirror human workflows (e.g., a calendar, an inbox, a notepad). This makes the agent's task more intuitive, improves security, and reduces prompt size.
- Before engineering a complex memory system, you must deeply understand your user and define the problem. Identify the specific 'wow factor' or core value proposition (e.g., proactivity, personalization) and design the memory system to enable that behavior. It's a system design problem, not just a prompt tuning exercise.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=-doV02eh8XI)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards

![image](https://github.com/user-attachments/assets/80f46b9a-22fe-4c0f-867d-5665cf619dab)

![image](https://github.com/user-attachments/assets/61902bb9-543d-48ad-910a-f085a1260cbb)

![image](https://github.com/user-attachments/assets/89af8e43-4a26-4e84-a263-6f0db0f99dd7)

![image](https://github.com/user-attachments/assets/42209c27-529a-47f6-8ded-0085c53a7417)

![image](https://github.com/user-attachments/assets/6d8d8a8c-c540-4fbc-a9d0-d25101b6f2af)


