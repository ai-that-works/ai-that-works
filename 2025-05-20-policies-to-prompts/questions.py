import json
import os
from pathlib import Path
from baml_client import b
from baml_client.types import Question
import asyncio

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))

def chunk_document(text: str, num_chunks: int = 5) -> list[str]:
    # Split the document into roughly equal chunks
    chunk_size = len(text) // num_chunks
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < num_chunks - 1 else len(text)
        chunks.append(text[start:end])
    return chunks

async def process_chunk(chunk: str, chunk_index: int) -> list[Question]:
    output_file = DATA_DIR / f"questions-{chunk_index}.json"
    
    # Check if we already have results for this chunk
    if output_file.exists():
        with open(output_file, "r") as f:
            try:
                return json.load(f)
            except Exception as e:
                print(f"Error loading {output_file}: {e}, reprocessing chunk")
    
    # Process the chunk
    questions = await b.ExtractQuestions(chunk)
    
    # Save chunk results
    with open(output_file, "w") as f:
        json.dump([x.model_dump(mode="json") for x in questions], f, indent=2)
    
    return questions

async def extract_questions(document: Path) -> None:
    # read the sox document
    with open(document, "r") as f:
        sox_document = f.read()

    # Check if we already have the final combined results
    if (DATA_DIR / "questions.json").exists():
        with open(DATA_DIR / "questions.json", "r") as f:
            try:
                questions = json.load(f)
                print(f"Loaded {len(questions)} questions from questions.json")
                return
            except Exception as e:
                print(f"Error loading questions.json: {e}, reprocessing all chunks")

    # Split document into chunks
    chunks = chunk_document(sox_document)
    
    # Process each chunk
    all_questions = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")
        chunk_questions = await process_chunk(chunk, i)
        all_questions.extend(chunk_questions)
    
    # Save combined results
    with open(DATA_DIR / "questions.json", "w") as f:
        json.dump([x.model_dump(mode="json") for x in all_questions], f, indent=2)
    
    print(f"Processed {len(all_questions)} total questions")

if __name__ == "__main__":
    asyncio.run(extract_questions(Path("data/sarbanes_oxley.htm")))
