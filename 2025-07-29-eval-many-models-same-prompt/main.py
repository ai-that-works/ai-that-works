from baml_client.async_client import b
from baml_client.types import VideoSummary, EmailStructure
from baml_py import ClientRegistry
import json
from typing import Tuple
import asyncio
from dotenv import load_dotenv
import os
from test_loader import load_test

target_dir = "results"

async def run_unit_test(test_name: str, model: str):
    summary, structure = load_test(test_name)
    cr = ClientRegistry()
    cr.set_primary(model)
    try:
        result = await b.DraftEmail(summary, structure, baml_options={ "cr": cr })
        unescaped_model = model.replace("/", "_")
        os.makedirs(f"{target_dir}/{test_name}", exist_ok=True)
        with open(f"{target_dir}/{test_name}/{unescaped_model}.json", "w") as f:
            json.dump(result.model_dump(mode="json"), f)
        return True
    except Exception as e:
        print(f"Model: {model}, Error: {e}")
        return False

async def main():
    models = ["openai/gpt-4o-mini", "anthropic/claude-3-5-sonnet-20240620", "MyGeminiSmart", "MyGemini"]
    tasks = [run_unit_test(test_name, model) for test_name in ["EmailStructure", "Burningguineafowl"] for model in models]
    results = await asyncio.gather(*tasks)
    print(results)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
