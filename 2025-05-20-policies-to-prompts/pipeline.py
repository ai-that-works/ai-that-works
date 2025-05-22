import asyncio
import json
from pathlib import Path
from baml_client.async_client import b
from asyncio import Semaphore
from baml_client.types import GiftEmailAnalysis
from baml_client.tracing import trace
from baml_py.errors import BamlValidationError
from typing import Literal
from tqdm import tqdm

max_concurrent_requests = 10
semaphore = Semaphore(max_concurrent_requests)

def mentions_gift(email: str) -> bool:
    return "gift" in email.lower()

def read_one_email(path: Path) -> str:
    with open(path, "r") as f:
        return f.read()

@trace
async def check_gift_email(email: str) -> GiftEmailAnalysis | Literal[False] | None:
    async with semaphore:
        if not mentions_gift(email):
            return None
        
        try:
            analysis = await b.EvaluateGiftPolicy(email, "Enron")
        except BamlValidationError:
            return False
        if analysis.type == "not_a_gift_email":
            return None
        if analysis.risk_level in {"high", "medium"}:
            return analysis
        return None

def load_emails_from_dir(path: Path) -> list[str]:
    emails = []
    for email_file in path.glob("**/_sent_mail/*"):
        if email_file.is_file():
            emails.append(read_one_email(email_file))
        if len(emails) > 100000:
            break
    return emails

@trace
async def check_emails(emails: list[str]):
    tasks = [check_gift_email(email) for email in emails]
    
    results = []
    with tqdm(total=len(tasks), desc="Analyzing emails") as pbar:
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            pbar.update(1)
    # count the number of True results
    print(f"Errors: {sum(1 for r in results if r is False)}")
    print(f"Number of emails that mention a gift: {sum(1 for r in results if r is not None)}")
    print(f"Number of emails that are high risk: {sum(1 for r in results if r is not None and r.risk_level == "high")}")
    print(f"Number of emails that are medium risk: {sum(1 for r in results if r is not None and r.risk_level == "medium")}")


    # Create output directories if they don't exist
    output_dir = Path("data/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories for different risk levels
    high_risk_dir = output_dir / "high_risk"
    medium_risk_dir = output_dir / "medium_risk"
    high_risk_dir.mkdir(exist_ok=True)
    medium_risk_dir.mkdir(exist_ok=True)

    # Write individual files for each flagged email
    for i, result in enumerate(results):
        if result is not None:
            # Create numbered subdirectory
            email_dir = high_risk_dir if result.risk_level == "high" else medium_risk_dir
            email_dir = email_dir / f"{i:04d}"
            email_dir.mkdir(exist_ok=True)

            # Write the analysis result
            with open(email_dir / "analysis.json", "w") as f:
                json.dump(result.model_dump(), f, indent=2)

            # Write the original email content
            with open(email_dir / "email.txt", "w") as f:
                f.write(emails[i])

if __name__ == "__main__":
    asyncio.run(check_emails(load_emails_from_dir(Path("data/enron_mail_20150507"))))