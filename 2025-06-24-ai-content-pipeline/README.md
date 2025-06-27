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

![image](https://github.com/user-attachments/assets/e61ac3b4-cc10-4e28-8547-a615ebc6f8e7)

![image](https://github.com/user-attachments/assets/a85aef4f-8101-40ec-86d8-e022f972fce1)

![image](https://github.com/user-attachments/assets/b899b5d6-e43b-4d06-a2fa-16d8e739e4d1)

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
