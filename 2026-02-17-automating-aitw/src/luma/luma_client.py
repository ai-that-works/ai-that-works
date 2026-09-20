"""Luma API client for fetching calendar events."""

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple
from urllib.parse import quote
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv

from src.luma.constants import (
    LUMA_BASE_URL,
    LOOKBACK_MONTHS,
    AI_THAT_WORKS_PREFIX,
    DEFAULT_TIMEZONE,
    DEFAULT_VISIBILITY,
    DEFAULT_MEETING_URL,
    FEEDBACK_EMAIL_ENABLED,
)

# Load environment variables
load_dotenv()


@dataclass
class Guest:
    """Represents a guest from a Luma event."""

    api_id: str
    user_api_id: str
    name: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    approval_status: str
    created_at: datetime
    invited_at: Optional[datetime]
    registered_at: Optional[datetime]
    joined_at: Optional[datetime]
    checked_in_at: Optional[datetime]
    check_in_qr_code: Optional[str]

    @classmethod
    def from_api_response(cls, entry: dict) -> "Guest":
        """
        Create a Guest from the API response entry.

        Args:
            entry: API response entry containing guest data

        Returns:
            Guest object
        """
        guest_data = entry.get("guest", entry)

        def parse_datetime(value: Optional[str]) -> Optional[datetime]:
            if value is None:
                return None
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        return cls(
            api_id=guest_data["api_id"],
            user_api_id=guest_data.get("user_api_id") or guest_data.get("user_id", ""),
            name=guest_data.get("name") or guest_data.get("user_name", ""),
            email=guest_data.get("email") or guest_data.get("user_email", ""),
            first_name=guest_data.get("user_first_name"),
            last_name=guest_data.get("user_last_name"),
            approval_status=guest_data.get("approval_status", ""),
            created_at=parse_datetime(guest_data["created_at"]),
            invited_at=parse_datetime(guest_data.get("invited_at")),
            registered_at=parse_datetime(guest_data.get("registered_at")),
            joined_at=parse_datetime(guest_data.get("joined_at")),
            checked_in_at=parse_datetime(guest_data.get("checked_in_at")),
            check_in_qr_code=guest_data.get("check_in_qr_code"),
        )


@dataclass
class CalendarContact:
    """Represents a contact on a Luma calendar (across all of its events)."""

    id: str
    user_id: Optional[str]
    email: str
    name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    event_approved_count: int
    created_at: Optional[datetime]

    @classmethod
    def from_api_response(cls, entry: dict) -> "CalendarContact":
        """
        Create a CalendarContact from the API response entry.

        Args:
            entry: API response entry containing contact data

        Returns:
            CalendarContact object
        """
        created_at = entry.get("created_at")

        return cls(
            id=entry.get("id", ""),
            user_id=entry.get("user_id"),
            email=entry.get("email") or "",
            name=entry.get("name"),
            first_name=entry.get("first_name"),
            last_name=entry.get("last_name"),
            event_approved_count=entry.get("event_approved_count") or 0,
            created_at=(
                datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if created_at
                else None
            ),
        )


@dataclass
class Event:
    """Represents a Luma calendar event."""

    api_id: str
    name: str
    description: str
    start_at: datetime
    end_at: datetime
    url: str
    meeting_url: Optional[str]
    cover_url: Optional[str]
    timezone: str
    visibility: str
    description_md: Optional[str] = None

    @property
    def clean_description(self) -> str:
        """
        Get the description with everything after 'Pre-reading' removed.

        Returns:
            Cleaned description string
        """
        if "🦄 ai that works" in self.description:
            self.description = self.description.split("🦄 ai that works")[1].strip()
        if "Pre-reading" in self.description:
            return self.description.split("Pre-reading")[0].strip()
        return self.description

    @classmethod
    def from_api_response(cls, entry: dict) -> "Event":
        """
        Create an Event from the API response entry.

        Args:
            entry: API response entry containing event data

        Returns:
            Event object
        """
        event_data = entry["event"]
        return cls(
            api_id=event_data["api_id"],
            name=event_data["name"],
            description=event_data["description"],
            start_at=datetime.fromisoformat(event_data["start_at"].replace("Z", "+00:00")),
            end_at=datetime.fromisoformat(event_data["end_at"].replace("Z", "+00:00")),
            url=event_data["url"],
            meeting_url=event_data.get("meeting_url"),
            cover_url=event_data.get("cover_url"),
            timezone=event_data["timezone"],
            visibility=event_data["visibility"],
            description_md=event_data.get("description_md"),
        )


class LumaClient:
    """Client for interacting with the Luma Calendar API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Luma client.

        Args:
            api_key: Luma API key. If not provided, reads from LUMA_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("LUMA_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Luma API key is required. Set LUMA_API_KEY environment variable or pass api_key parameter."
            )

        self.base_url = LUMA_BASE_URL

    def _get_lookback_date(self, months: int = LOOKBACK_MONTHS) -> datetime:
        """
        Calculate the date to look back from today.

        Args:
            months: Number of months to look back (default: LOOKBACK_MONTHS)

        Returns:
            Datetime object representing the lookback date
        """
        today = datetime.now(timezone.utc)
        # Approximate months as 30 days each for simplicity
        lookback_date = today - timedelta(days=months * 30)
        return lookback_date

    def list_events(self, after: Optional[datetime] = None) -> List[Event]:
        """
        List calendar events after a specific date.

        Args:
            after: Start date for event search. If not provided, uses LOOKBACK_MONTHS from today.

        Returns:
            List of Event objects
        """
        if after is None:
            after = self._get_lookback_date()

        # Format datetime to ISO 8601 and URL encode
        after_str = after.isoformat()
        after_encoded = quote(after_str, safe="")

        url = f"{self.base_url}/calendar/list-events?after={after_encoded}"
        headers = {"accept": "application/json", "x-luma-api-key": self.api_key}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        events = [Event.from_api_response(entry) for entry in data.get("entries", [])]

        return events

    def get_next_ai_that_works_event(self) -> Optional[Event]:
        """
        Get the next upcoming 'ai that works' event.

        Returns:
            The next upcoming Event with "🦄 ai that works" in the name, or None if not found
        """
        events = self.list_events()
        now = datetime.now(timezone.utc)

        # Filter for "🦄 ai that works" events that haven't started yet
        ai_works_events = [
            event
            for event in events
            if AI_THAT_WORKS_PREFIX in event.name and event.start_at > now
        ]

        if not ai_works_events:
            return None

        # Sort by start_at ascending (soonest first)
        ai_works_events.sort(key=lambda e: e.start_at)

        return ai_works_events[0]

    def get_most_recent_ai_that_works_event(self) -> Optional[Event]:
        """
        Get the most recent past 'ai that works' event.

        Returns:
            The most recent past Event with "🦄 ai that works" in the name, or None if not found
        """
        events = self.list_events()
        now = datetime.now(timezone.utc)

        # Filter for past "🦄 ai that works" events
        ai_works_events = [
            event
            for event in events
            if AI_THAT_WORKS_PREFIX in event.name and event.start_at < now
        ]

        if not ai_works_events:
            return None

        # Sort by start_at descending (most recent first)
        ai_works_events.sort(key=lambda e: e.start_at, reverse=True)
        return ai_works_events[0]

    def list_calendar_contacts(
        self, page_limit: int = 100, max_contacts: Optional[int] = None
    ) -> List["CalendarContact"]:
        """
        List every contact on the calendar, following pagination to the end.

        Args:
            page_limit: Contacts to request per page
            max_contacts: Stop after this many contacts (useful for testing)

        Returns:
            List of CalendarContact objects
        """
        url = f"{self.base_url}/calendars/contacts/list"
        headers = {"accept": "application/json", "x-luma-api-key": self.api_key}

        contacts: List[CalendarContact] = []
        cursor: Optional[str] = None

        while True:
            params = {"pagination_limit": page_limit}
            if cursor:
                params["pagination_cursor"] = cursor

            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            contacts.extend(
                CalendarContact.from_api_response(entry)
                for entry in data.get("entries", [])
            )

            if max_contacts is not None and len(contacts) >= max_contacts:
                return contacts[:max_contacts]

            cursor = data.get("next_cursor")
            if not data.get("has_more") or not cursor:
                return contacts

    def get_guests(self, event_id: str) -> List[Guest]:
        """
        Get the guest list for an event.

        Args:
            event_id: The API ID of the event

        Returns:
            List of Guest objects
        """
        url = f"{self.base_url}/event/get-guests?event_id={event_id}"
        headers = {"accept": "application/json", "x-luma-api-key": self.api_key}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        guests = [Guest.from_api_response(entry) for entry in data.get("entries", [])]

        return guests

    def get_most_recent_ai_that_works_event_guests(self) -> List[Guest]:
        """
        Get the guest list for the most recent past 'ai that works' event.

        Returns:
            List of Guest objects, or empty list if no event found
        """
        event = self.get_most_recent_ai_that_works_event()
        if event is None:
            return []
        return self.get_guests(event.api_id)

    def upload_cover_image(self, image_path: str) -> str:
        """
        Upload a cover image and return the CDN URL.

        Args:
            image_path: Path to the image file to upload

        Returns:
            The CDN URL of the uploaded image
        """
        # Step 1: Get upload URL
        url = f"{self.base_url}/images/create-upload-url"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-luma-api-key": self.api_key,
        }
        payload = {"purpose": "event-cover"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        upload_url = data["upload_url"]
        file_url = data["file_url"]

        # Step 2: Upload image to S3
        with open(image_path, "rb") as f:
            image_data = f.read()

        upload_response = requests.put(
            upload_url,
            data=image_data,
            headers={"Content-Type": "image/png"},
        )
        upload_response.raise_for_status()

        return file_url

    def _format_slug(self, luma_url_suffix: str) -> str:
        """
        Format a URL suffix into a valid slug.

        Args:
            luma_url_suffix: The URL suffix to format

        Returns:
            Formatted slug (lowercase, spaces and underscores replaced with dashes)
        """
        return luma_url_suffix.lower().replace("_", "-").replace(" ", "-")

    def _check_slug_available(self, slug: str) -> bool:
        """
        Check if a slug is available for use.

        Args:
            slug: The slug to check

        Returns:
            True if the slug is available, False otherwise
        """
        url = f"{self.base_url}/entity/lookup?slug={slug}"
        headers = {
            "accept": "application/json",
            "x-luma-api-key": self.api_key,
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("entity") is None

    def _verify_tuesday(self, event_date: date) -> None:
        """
        Verify that the given date is a Tuesday.

        Args:
            event_date: The date to verify

        Raises:
            ValueError: If the date is not a Tuesday
        """
        # weekday() returns 0 for Monday, 1 for Tuesday, etc.
        if event_date.weekday() != 1:
            day_name = event_date.strftime("%A")
            raise ValueError(
                f"Event date must be a Tuesday, but {event_date} is a {day_name}."
            )

    def _create_event_times(self, event_date: date) -> Tuple[datetime, datetime]:
        """
        Create start and end times for an event on the given date.

        Events are always 10:15-11:15 AM PST.

        Args:
            event_date: The date of the event

        Returns:
            Tuple of (start_at, end_at) as UTC datetimes
        """
        pst = ZoneInfo("America/Los_Angeles")

        # Create 10:15 AM and 11:15 AM in PST
        start_local = datetime(
            event_date.year, event_date.month, event_date.day, 10, 15, 0, tzinfo=pst
        )
        end_local = datetime(
            event_date.year, event_date.month, event_date.day, 11, 15, 0, tzinfo=pst
        )

        # Convert to UTC
        start_utc = start_local.astimezone(timezone.utc)
        end_utc = end_local.astimezone(timezone.utc)

        return start_utc, end_utc

    def create_event(
        self,
        name: str,
        description_md: str,
        event_date: date,
        cover_url: str,
        luma_url_suffix: str,
    ) -> dict:
        """
        Create a new event.

        Args:
            name: Event name/title
            description_md: Event description in markdown format
            event_date: The date of the event (must be a Tuesday)
            cover_url: URL of the cover image
            luma_url_suffix: URL suffix for the event page (will be formatted as slug)

        Returns:
            API response containing the created event data

        Raises:
            ValueError: If the date is not a Tuesday or if the slug is already in use
        """
        # Verify date is a Tuesday
        self._verify_tuesday(event_date)

        # Create start and end times (10-11 AM PST)
        start_at, end_at = self._create_event_times(event_date)

        # Format and validate slug
        slug = self._format_slug(luma_url_suffix)
        if not self._check_slug_available(slug):
            raise ValueError(
                f"The slug '{slug}' is already in use. Please pick a different luma_url_suffix."
            )

        api_url = f"{self.base_url}/event/create"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-luma-api-key": self.api_key,
        }

        # Format datetimes to ISO format with Z suffix
        def format_datetime(dt: datetime) -> str:
            iso = dt.isoformat()
            # Remove any existing timezone suffix and add Z
            if "+" in iso:
                iso = iso.split("+")[0]
            return iso + "Z"

        payload = {
            "name": name,
            "description_md": description_md,
            "start_at": format_datetime(start_at),
            "end_at": format_datetime(end_at),
            "cover_url": cover_url,
            "timezone": DEFAULT_TIMEZONE,
            "visibility": DEFAULT_VISIBILITY,
            "feedback_email": {"enabled": FEEDBACK_EMAIL_ENABLED},
            "meeting_url": DEFAULT_MEETING_URL,
            "zoom_meeting_url": DEFAULT_MEETING_URL,
            "slug": slug,
        }

        response = requests.post(api_url, json=payload, headers=headers)
        if not response.ok:
            print(f"Error response: {response.text}")
        response.raise_for_status()
        return response.json()

    def create_ai_that_works_event(
        self,
        name: str,
        description_md: str,
        event_date: date,
        cover_image_path: str,
        luma_url_suffix: str,
    ) -> dict:
        """
        Create a new 'ai that works' event with cover image upload.

        Args:
            name: Event name/title
            description_md: Event description in markdown format
            event_date: The date of the event (must be a Tuesday)
            cover_image_path: Path to the cover image file
            luma_url_suffix: URL suffix for the event page (will be formatted as slug)

        Returns:
            API response containing the created event data

        Raises:
            ValueError: If the date is not a Tuesday or if the slug is already in use
        """
        # Upload cover image
        cover_url = self.upload_cover_image(cover_image_path)

        # Create event using constants for defaults
        return self.create_event(
            name=name,
            description_md=description_md,
            event_date=event_date,
            cover_url=cover_url,
            luma_url_suffix=luma_url_suffix,
        )
