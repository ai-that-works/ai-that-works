"""Loops.so API client for reading mailing lists and creating contacts."""

import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

from src.loops.constants import (
    LOOPS_BASE_URL,
    LOOPS_REQUESTS_PER_SECOND,
    LOOPS_MAX_RETRIES,
    LOOPS_BACKOFF_SECONDS,
    LOOPS_TIMEOUT_SECONDS,
)

# Load environment variables
load_dotenv()


@dataclass
class MailingList:
    """Represents a mailing list in Loops."""

    id: str
    name: str
    description: Optional[str]
    is_public: bool

    @classmethod
    def from_api_response(cls, entry: dict) -> "MailingList":
        """
        Create a MailingList from the API response entry.

        Args:
            entry: API response entry containing mailing list data

        Returns:
            MailingList object
        """
        return cls(
            id=entry["id"],
            name=entry["name"],
            description=entry.get("description"),
            is_public=entry.get("isPublic", False),
        )


class LoopsClient:
    """Client for the Loops.so v1 API.

    This client deliberately exposes no update path. The sync only ever reads
    (to check for an existing contact) or creates (for addresses Loops has
    never seen), so there is no code path that can overwrite a contact that
    already exists in the audience.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Loops client.

        Args:
            api_key: Loops API key. If not provided, reads from LOOPS_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("LOOPS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Loops API key is required. Set LOOPS_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = LOOPS_BASE_URL
        self._min_interval = 1.0 / LOOPS_REQUESTS_PER_SECOND
        self._last_request_at = 0.0
        # A session keeps the TLS connection warm across thousands of lookups.
        self._session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        """Build the auth headers for an API request."""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }

    def _throttle(self) -> None:
        """Sleep as needed to stay under the Loops rate limit."""
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_at = time.monotonic()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        Make a rate-limited API request, retrying on 429, 5xx, and network errors.

        Read timeouts and dropped connections are expected over a run of a few
        thousand lookups, so they are retried rather than allowed to abort the
        caller.

        Args:
            method: HTTP method
            path: Path below the API base URL (e.g. "/contacts/find")
            **kwargs: Passed through to requests.request

        Returns:
            The successful Response object

        Raises:
            requests.RequestException: If the request fails after all retries
        """
        url = f"{self.base_url}{path}"
        last_error: Optional[Exception] = None

        for attempt in range(LOOPS_MAX_RETRIES):
            self._throttle()

            try:
                response = self._session.request(
                    method,
                    url,
                    headers=self._headers(),
                    timeout=LOOPS_TIMEOUT_SECONDS,
                    **kwargs,
                )
            except requests.RequestException as exc:
                last_error = exc
                if attempt == LOOPS_MAX_RETRIES - 1:
                    raise
                time.sleep(LOOPS_BACKOFF_SECONDS * (2**attempt))
                continue

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == LOOPS_MAX_RETRIES - 1:
                    break
                time.sleep(LOOPS_BACKOFF_SECONDS * (2**attempt))
                continue

            response.raise_for_status()
            return response

        if last_error is not None:
            raise last_error

        response.raise_for_status()
        return response

    def list_mailing_lists(self) -> List[MailingList]:
        """
        List the account's mailing lists.

        Returns:
            List of MailingList objects
        """
        response = self._request("GET", "/lists")
        return [MailingList.from_api_response(entry) for entry in response.json()]

    def contact_exists(self, email: str) -> bool:
        """
        Check whether Loops already has a contact with this email address.

        Args:
            email: Email address to look up

        Returns:
            True if a contact already exists, False otherwise
        """
        response = self._request("GET", "/contacts/find", params={"email": email})
        results = response.json()
        return bool(results)

    def create_contact(
        self,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        mailing_list_ids: Optional[List[str]] = None,
        source: Optional[str] = None,
    ) -> str:
        """
        Create a new contact.

        Only non-empty fields are sent, and this endpoint never updates an
        existing contact: Loops returns an error if the email is already in
        the audience.

        Args:
            email: Email address (required)
            first_name: Contact's first name, if known
            last_name: Contact's last name, if known
            mailing_list_ids: Mailing lists to subscribe the new contact to
            source: Source label shown in the Loops UI

        Returns:
            The new contact's Loops ID
        """
        payload: Dict[str, object] = {"email": email}

        if first_name:
            payload["firstName"] = first_name
        if last_name:
            payload["lastName"] = last_name
        if source:
            payload["source"] = source
        if mailing_list_ids:
            payload["mailingLists"] = {list_id: True for list_id in mailing_list_ids}

        response = self._request("POST", "/contacts/create", json=payload)
        return response.json().get("id", "")
