"""Loops.so API integration module."""

from .loops_client import LoopsClient, MailingList
from .constants import LOOPS_BASE_URL, LOOPS_REQUESTS_PER_SECOND

__all__ = [
    "LoopsClient",
    "MailingList",
    "LOOPS_BASE_URL",
    "LOOPS_REQUESTS_PER_SECOND",
]
