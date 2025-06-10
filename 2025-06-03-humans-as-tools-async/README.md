# Humans as Tools: Async Agents and Durable Execution

[![video thumbnail](video thumbnail)](video link)

This session builds on our [12-factor agents workshop](../2025-04-22-twelve-factor-agents) to explore async agents and durable execution patterns. We'll learn how to build agents that can pause, contact humans for feedback or approval, and resume execution based on human responses.

## What You'll Learn

- How to implement async agent patterns with human-in-the-loop workflows
- State management for durable agent execution
- Different channels for human interaction (CLI, HTTP, email)
- Webhook integration for non-blocking human approvals
- Testing strategies for async agent workflows

## Key Takeaways

- Two types of human interaction - deterministic (code enforces human approval) and non-deterministic (agent chooses to contact a human)
- approver might not be the person interacting with the chatbot
- State management is key to building agents that can pause/resume for human interaction
- Separate concerns of inner loop (agent) and outer loop (human interaction)

## Whiteboards





## Running the Code

- Basic TypeScript knowledge
- Node.js 20+ installed
- Understanding of async/await patterns
- Familiarity with HTTP APIs and webhooks
- OPENAI_API_KEY env var set

### Quick Setup

```bash
# Install dependencies
npm install

# Run the final version w/ cli
npx tsx src/index.ts

# OR run the final version w/ http
npx tsx src/server.ts
```



