import json
from typing import Tuple
from baml_client.types import VideoSummary, EmailStructure

def load_test(name: str) -> Tuple[VideoSummary, EmailStructure]:
    with open(f"tests/{name}.json", "r") as f:
        data = json.load(f)
        video_summary = data[0]  # First element as VideoSummary
        email_structure = data[1]  # Second element as EmailStructure
        return VideoSummary(**video_summary), EmailStructure(**email_structure)