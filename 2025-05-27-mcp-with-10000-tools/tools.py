import json
from typing import Any, Awaitable, Dict

import openai
from baml_client.type_builder import TypeBuilder
from parse_json_schema import TOOL_NAME_KEY, parse_tools
from baml_client import b
from baml_client.types import HumanMessage, Actions
from baml_py.baml_py import FieldType
import numpy as np
import asyncio


async def load_tools(query: str, tool_file_path: str) -> TypeBuilder:
    tb = TypeBuilder()
    tools = parse_tools(tool_file_path, tb)
    tool_types = list(tools.values())[:100]
    tool_options = tb.union(await _narrow_down_categories(query, tool_types))
    tb.Actions.add_property("tools", tool_options)
    return tb

client = openai.AsyncOpenAI()

async def embed(text: str) -> list[float]:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

async def _narrow_down_categories(text: str, tools: list[tuple[FieldType, Dict[str, Any]]]) -> list[FieldType]:
    embeddings: list[tuple[FieldType, Awaitable[list[float]]]] = []
    for category in tools:
        embeddings.append((category[0], embed(json.dumps(category[1]))))
    embedding_caught = await asyncio.gather(*[e[1] for e in embeddings])

    text_embedding = await embed(text)
    best_matches: list[tuple[FieldType, float]] = []
    for category, embedding in zip(embeddings, embedding_caught):
        cosine_similarity = np.dot(text_embedding, embedding) / (np.linalg.norm(text_embedding) * np.linalg.norm(embedding))
        best_matches.append((category[0], cosine_similarity))
    max_matches = 10
    matches = sorted(best_matches, key=lambda x: x[1], reverse=True)[:max_matches]
    return [match[0] for match in matches]

def narrow_tools(query: str, tools: list[FieldType]) -> list[FieldType]:
    return tools[:50]

def sort_actions(actions: list[Actions | HumanMessage]) -> list[Actions | HumanMessage]:
    return sorted(actions, key=lambda x: isinstance(x, HumanMessage))

async def dosomething():
    
    chat = [
        "User: get pages 1-3 from the database",
    ]
    while True:
        tb = await load_tools(chat[-1], "tools.json")
        action = await b.PickAction("\n".join(chat), { "tb": tb })
        if isinstance(action, HumanMessage):
            print(action.message)
            next_message = input("Enter a message: ")
            chat.append(f"Assistant: {next_message}")
            chat.append(f"User: {next_message}")
        else:
            assert action.model_extra 
            tool: Dict[str, Any] = action.model_extra["tools"]
            tool_name = tool.pop(TOOL_NAME_KEY)
            tool_args = tool
            print(f"I'd like to call tool: {tool_name}")
            print(f"{json.dumps(tool_args, indent=2)}")
            break

if __name__ == "__main__":
    asyncio.run(dosomething())
