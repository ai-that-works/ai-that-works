from pathlib import Path
import pytest
from pipeline import check_gift_email

test_cases = [
    {
        "email": "data/enron_mail_20150507/mcconnell-m/_sent_mail/568.",
        "expected_result": "high"
    },
]

@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", test_cases)
async def test_pipeline(test_case):
    path = Path(__file__).parent / test_case["email"]  # noqa: F821
    with open(path, "r") as f:
        email_content = f.read()
    result = await check_gift_email(email_content)
    assert result is not None
    assert result.risk_level == test_case["expected_result"]

if __name__ == "__main__":
    pytest.main()
