#!/usr/bin/env python3
import os
from pathlib import Path
from baml_client import b
import sys
import asyncio
from tqdm import tqdm

CHUNK_SIZE = 1000

async def redact_pii_in_text(text: str) -> str:
    """Use BAML RedactPII to redact sensitive information asynchronously"""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, b.RedactPII, text)
        return result
    except Exception as e:
        print(f"Error redacting PII: {e}")
        return text  # Return original if error

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE):
    """Yield successive chunk_size character chunks from text."""
    for i in range(0, len(text), chunk_size):
        yield text[i:i+chunk_size]

async def process_file(input_path: Path, output_path: Path, file_pbar: tqdm):
    """Process a single file to redact PII in 1000-character chunks asynchronously."""
    print(f"\nProcessing: {input_path.name}")
    try:
        with open(input_path, 'r') as f:
            content = f.read()

        chunks = list(chunk_text(content))
        chunk_indices = list(range(len(chunks)))
        chunk_pbar = tqdm(total=len(chunks), desc=f"Chunks {input_path.name}", leave=False)

        async def redact_and_update(idx, chunk):
            redacted = await redact_pii_in_text(chunk)
            chunk_pbar.update(1)
            return idx, redacted

        # Schedule all chunk redactions in parallel
        tasks = [redact_and_update(idx, chunk) for idx, chunk in enumerate(chunks)]
        redacted_results = await asyncio.gather(*tasks)
        chunk_pbar.close()

        # Sort by original chunk order
        redacted_results.sort(key=lambda x: x[0])
        redacted_content = ''.join([r[1] for r in redacted_results])

        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(redacted_content)
        print(f"  ✓ Saved to: {output_path}")
    except Exception as e:
        print(f"  ❌ Error processing {input_path.name}: {e}")
    finally:
        file_pbar.update(1)

def main():
    raw_dir = Path("raw")
    processed_dir = Path("processed")
    processed_dir.mkdir(exist_ok=True)
    thread_files = sorted(raw_dir.glob("thread_*.txt"))
    if not thread_files:
        print("No thread files found in raw/ directory")
        return
    print(f"Found {len(thread_files)} thread files to process")

    async def process_all():
        file_pbar = tqdm(total=len(thread_files), desc="Files", leave=True)
        tasks = [process_file(thread_file, processed_dir / thread_file.name, file_pbar) for thread_file in thread_files]
        await asyncio.gather(*tasks)
        file_pbar.close()
        print(f"\n✅ Processing complete! Redacted files saved to {processed_dir}/")

    asyncio.run(process_all())

if __name__ == "__main__":
    main()