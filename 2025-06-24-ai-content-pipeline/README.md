# Building an AI Content Pipeline

> Content creation involves a lot of manual work - uploading videos, sending emails, and other follow-up tasks that are easy to drop. We'll build an agent that integrates YouTube, email, GitHub and human-in-the-loop to fully automate the AI that Works content pipeline, handling all the repetitive work while maintaining quality.

[Video](https://www.youtube.com/watch?v=Xece-W7Xf48) (1h15m)

[![Building an AI Content Pipeline](https://img.youtube.com/vi/Xece-W7Xf48/0.jpg)](https://www.youtube.com/watch?v=Xece-W7Xf48)

## Key Points

1. **Start with infrastructure and basic pipeline before optimizing AI components**
2. **Use real data for testing rather than synthetic examples**
3. **Consider breaking complex generations into multiple steps**
4. **Build systems that allow fast iteration on prompts**
5. **Think carefully about type safety and data consistency across the stack**

## Key Topics

- AI Pipeline Architecture
- Type Safety in AI Systems
- Prompt Engineering
- Real-time Data Streaming
- Testing AI Systems
- Content Generation

## Main Takeaways

- Build infrastructure first before focusing on AI components - having a working pipeline is critical for iteration
- Avoid unnecessary frameworks and focus on simple, controllable code that gives you full flexibility
- Use real data for testing and iteration rather than synthetic examples
- Consider type safety and data consistency across the full stack when building AI pipelines

## Whiteboards

[Space for whiteboard graphics to be added]

## Core Architecture

### 🏗️ Infrastructure Foundation
- Laid the foundation with a solid infrastructure, the key to your AI success
- Focus on building a robust pipeline that can handle various content types and sources

### 🚀 Automation Features
- Automate your video uploads straight from Zoom with ease
- Integrate with YouTube API for seamless content publishing
- GitHub integration for code and documentation management

### ✍️ Content Generation
- Craft transcripts, draft emails, & iterate on AI models effortlessly—and faster!
- Use BAML for structured prompt engineering
- Build pipelines that allow rapid iteration on content generation

## Email Summary

Here's what we covered in this session:
- 🏗️ Laid the foundation with a solid infrastructure, the key to your AI success.
- 🚀 Automate your video uploads straight from Zoom with ease.
- ✍️ Craft transcripts, draft emails, & iterate on AI models effortlessly—and faster!

Takeaways you can't miss:
- Kickstart with a structured pipeline to power-up your AI components. ⚡
- Run tests on real data for precision and efficiency.
- Break down the complicated tasks into chewable bits for optimal control and results.

## Running the Code

```bash
# Backend setup
cd backend
uv sync
cp env.template .env
# Configure your environment variables

# Frontend setup
cd frontend
npm install
npm run dev

# Run the full pipeline
uv run python main.py
```

## Resources

- [Session Recording](https://www.youtube.com/watch?v=Xece-W7Xf48)
- [BAML Documentation](https://docs.boundaryml.com/)
- [Discord Community](https://www.boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)