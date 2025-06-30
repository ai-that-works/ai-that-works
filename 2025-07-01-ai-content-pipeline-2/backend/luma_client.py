import os
import requests
from typing import Optional, List
from datetime import datetime, timezone
import logging
from models import LumaEvent

logger = logging.getLogger(__name__)


class LumaClient:
    def __init__(self):
        self.api_key = os.getenv("LUMA_API_KEY")
        if not self.api_key:
            logger.warning("LUMA_API_KEY not found in environment variables")
        self.base_url = "https://public-api.lu.ma/public/v1"
        self.headers = {"accept": "application/json", "x-luma-api-key": self.api_key}

    def get_event_for_zoom_meeting(self, zoom_meeting_id: str) -> Optional[LumaEvent]:
        """
        Get the Luma event for a specific Zoom meeting by:
        1. Getting Zoom recording details to find the date
        2. Matching against Luma events by date AND zoom URL

        Returns the matching Luma event or None if not found.
        """
        if not self.api_key:
            logger.error("LUMA_API_KEY not configured")
            return None

        try:
            logger.info(
                f"Getting event for Zoom meeting ID: {zoom_meeting_id} (type: {type(zoom_meeting_id)})"
            )

            # First, get the Zoom recording details to find the date
            from zoom_client import zoom_client

            recordings = zoom_client.get_recordings()
            zoom_recording = None

            logger.info(f"Found {len(recordings)} total Zoom recordings")

            for rec in recordings:
                # Log the comparison for debugging
                rec_meeting_id = rec["meeting_id"]
                logger.debug(
                    f"Comparing {rec_meeting_id} (type: {type(rec_meeting_id)}) with {zoom_meeting_id}"
                )

                if str(rec_meeting_id) == str(zoom_meeting_id):
                    zoom_recording = rec
                    logger.info(
                        f"Found matching Zoom recording: {rec.get('meeting_title')}"
                    )
                    break

            if not zoom_recording:
                logger.warning(
                    f"No Zoom recording found for meeting ID: {zoom_meeting_id}"
                )
                logger.warning(
                    f"Available meeting IDs: {[rec['meeting_id'] for rec in recordings[:5]]}..."
                )  # Show first 5
                return None

            # Parse recording date
            recording_start = zoom_recording.get("recording_start")
            if not recording_start:
                logger.warning(
                    f"No recording start time for Zoom meeting: {zoom_meeting_id}"
                )
                return None

            try:
                recording_date = datetime.fromisoformat(
                    recording_start.replace("Z", "+00:00")
                )
            except Exception as e:
                logger.error(f"Error parsing recording date: {e}")
                return None

            # Now get matching Luma event by date and URL
            return self._get_event_by_zoom_date_and_url(recording_date, zoom_meeting_id)

        except Exception as e:
            logger.error(
                f"Error getting Luma event for Zoom meeting {zoom_meeting_id}: {e}"
            )
            return None

    def _get_recent_past_events(self, limit: int = 10) -> List[LumaEvent]:
        """Get the most recent past events from Luma API

        Example Luma event payload structure:
        {
          "api_id": "evt-7AfHSGOBmoz4iLO",
          "event": {
            "api_id": "evt-7AfHSGOBmoz4iLO",
            "calendar_api_id": "cal-NQYQhHfQN7sg4BF",
            "created_at": "2025-06-10T18:45:52.693Z",
            "cover_url": "https://images.lumacdn.com/event-covers/2a/5856fd94-de13-4f1f-94d0-8e72da4e8710.png",
            "name": "🦄 ai that works: Memory from scratch",
            "description": "🦄 ai that works\\n\\n\\n\\nWe've all heard a lot about memory...",
            "description_md": "🦄 ai that works\\n\\n> A weekly conversation...",
            "start_at": "2025-07-08T17:00:00.000Z",
            "duration_interval": "P0Y0M0DT1H0M0S",
            "end_at": "2025-07-08T18:00:00.000Z",
            "geo_address_json": null,
            "geo_latitude": null,
            "geo_longitude": null,
            "url": "https://lu.ma/7sfm30gu",
            "timezone": "America/Los_Angeles",
            "user_api_id": "usr-gf7C8MCpjOWZjQW",
            "visibility": "public",
            "meeting_url": "https://us06web.zoom.us/j/84317818466?pwd=8LWFhSv4sbN6OVkhdjEdHio7O9Bxyo.1",
            "zoom_meeting_url": "https://us06web.zoom.us/j/84317818466?pwd=8LWFhSv4sbN6OVkhdjEdHio7O9Bxyo.1"
          },
          "tags": []
        }
        """
        if not self.api_key:
            logger.error("LUMA_API_KEY not configured")
            return []

        try:
            url = f"{self.base_url}/calendar/list-events"

            logger.info(f"Fetching recent past events from Luma (limit: {limit})")
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])

                # Parse and filter past events
                past_events = []
                now = datetime.now(timezone.utc)

                for entry in entries:
                    event = entry.get("event", {})

                    # Parse start time
                    start_at_str = event.get("start_at")
                    if start_at_str:
                        try:
                            start_at = datetime.fromisoformat(
                                start_at_str.replace("Z", "+00:00")
                            )

                            # Only include past events
                            if start_at < now:
                                luma_event = LumaEvent(
                                    event_id=event.get("api_id", ""),
                                    title=event.get("name", ""),
                                    thumbnail_url=event.get("cover_url"),
                                    description=event.get("description"),
                                    url=event.get("url"),
                                    start_at=start_at,
                                    end_at=datetime.fromisoformat(
                                        event.get("end_at").replace("Z", "+00:00")
                                    )
                                    if event.get("end_at")
                                    else None,
                                )
                                past_events.append(luma_event)
                        except Exception as e:
                            logger.warning(f"Error parsing event date: {e}")

                # Sort by start time descending (most recent first)
                past_events.sort(key=lambda x: x.start_at, reverse=True)

                # Return only the requested number of events
                result = past_events[:limit]
                logger.info(f"Found {len(result)} recent past events")
                return result
            else:
                logger.error(
                    f"Luma API error: {response.status_code} - {response.text}"
                )
                return []

        except Exception as e:
            logger.error(f"Error fetching events from Luma: {e}")
            return []

    def _get_event_by_zoom_date_and_url(
        self, zoom_recording_date: datetime, zoom_meeting_id: str
    ) -> Optional[LumaEvent]:
        """
        Find a Luma event that matches both the Zoom recording date AND contains the Zoom meeting ID in its URL/description.
        Returns the matching Luma event.
        """
        logger.info(
            f"Looking up Luma event for Zoom recording date: {zoom_recording_date.date()} and meeting ID: {zoom_meeting_id}"
        )

        # First, try to get the event data with zoom URLs from the API
        try:
            url = f"{self.base_url}/calendar/list-events"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])

                # Compare only the date part
                zoom_date = zoom_recording_date.date()
                now = datetime.now(timezone.utc)

                for entry in entries:
                    event_data = entry.get("event", {})

                    # Parse start time
                    start_at_str = event_data.get("start_at")
                    if start_at_str:
                        try:
                            start_at = datetime.fromisoformat(
                                start_at_str.replace("Z", "+00:00")
                            )
                            event_date = start_at.date()

                            # Check if date matches
                            if event_date == zoom_date and start_at < now:
                                event_name = event_data.get("name", "Unknown")
                                logger.debug(
                                    f"Checking event '{event_name}' on {event_date}"
                                )

                                # Check meeting_url or zoom_meeting_url fields
                                meeting_url = (
                                    event_data.get("meeting_url")
                                    or event_data.get("zoom_meeting_url")
                                    or ""
                                )

                                # Extract meeting ID from Zoom URL if present
                                if meeting_url and "zoom.us" in meeting_url:
                                    logger.debug(
                                        f"Found Zoom URL in event: {meeting_url}"
                                    )
                                    # Extract meeting ID from URL like: https://us06web.zoom.us/j/84317818466?pwd=...
                                    import re

                                    match = re.search(r"/j/(\d+)", meeting_url)
                                    if match:
                                        url_meeting_id = match.group(1)
                                        logger.info(
                                            f"Extracted meeting ID {url_meeting_id} from URL: {meeting_url}"
                                        )
                                        logger.info(
                                            f"Comparing extracted ID '{url_meeting_id}' with zoom ID '{zoom_meeting_id}'"
                                        )

                                        if str(url_meeting_id) == str(zoom_meeting_id):
                                            logger.info(
                                                f"Found exact matching Luma event: {event_data.get('name')} on {event_date}"
                                            )
                                            return LumaEvent(
                                                event_id=event_data.get("api_id", ""),
                                                title=event_data.get("name", ""),
                                                thumbnail_url=event_data.get(
                                                    "cover_url"
                                                ),
                                                description=event_data.get(
                                                    "description"
                                                ),
                                                url=event_data.get("url"),
                                                start_at=start_at,
                                                end_at=datetime.fromisoformat(
                                                    event_data.get("end_at").replace(
                                                        "Z", "+00:00"
                                                    )
                                                )
                                                if event_data.get("end_at")
                                                else None,
                                            )

                                # Also check if meeting ID is in description or regular URL
                                if (
                                    zoom_meeting_id in (event_data.get("url") or "")
                                ) or (
                                    zoom_meeting_id
                                    in (event_data.get("description") or "")
                                ):
                                    logger.info(
                                        f"Found matching Luma event via description/URL: {event_data.get('name')} on {event_date}"
                                    )
                                    return LumaEvent(
                                        event_id=event_data.get("api_id", ""),
                                        title=event_data.get("name", ""),
                                        thumbnail_url=event_data.get("cover_url"),
                                        description=event_data.get("description"),
                                        url=event_data.get("url"),
                                        start_at=start_at,
                                        end_at=datetime.fromisoformat(
                                            event_data.get("end_at").replace(
                                                "Z", "+00:00"
                                            )
                                        )
                                        if event_data.get("end_at")
                                        else None,
                                    )

                        except Exception as e:
                            logger.warning(f"Error parsing event date: {e}")

        except Exception as e:
            logger.error(f"Error fetching events for matching: {e}")

        logger.warning(
            f"No Luma event found for date: {zoom_date} with Zoom ID: {zoom_meeting_id}"
        )
        return None

    async def fetch_next_upcoming_event(self) -> Optional[LumaEvent]:
        """
        Fetch all events, filter to future ones, and use BAML to identify the next AI that works event
        """
        if not self.api_key:
            logger.error("LUMA_API_KEY not configured")
            return None

        try:
            # Fetch all events
            url = f"{self.base_url}/calendar/list-events"

            logger.info("Fetching all events from Luma to find next upcoming")
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                logger.error(
                    f"Luma API error: {response.status_code} - {response.text}"
                )
                return None

            data = response.json()
            entries = data.get("entries", [])

            # Filter to future events
            future_events = []
            now = datetime.now(timezone.utc)

            for entry in entries:
                event = entry.get("event", {})

                # Parse start time
                start_at_str = event.get("start_at")
                if start_at_str:
                    try:
                        start_at = datetime.fromisoformat(
                            start_at_str.replace("Z", "+00:00")
                        )

                        # Only include future events
                        if start_at > now:
                            luma_event = LumaEvent(
                                event_id=event.get("api_id", ""),
                                title=event.get("name", ""),
                                thumbnail_url=event.get("cover_url"),
                                description=event.get("description"),
                                url=event.get("url"),
                                start_at=start_at,
                                end_at=datetime.fromisoformat(
                                    event.get("end_at").replace("Z", "+00:00")
                                )
                                if event.get("end_at")
                                else None,
                            )
                            future_events.append(luma_event)
                    except Exception as e:
                        logger.warning(f"Error parsing event date: {e}")

            if not future_events:
                logger.info("No future events found")
                return None

            # Sort by start time ascending (earliest first)
            future_events.sort(key=lambda x: x.start_at)

            # Use BAML to identify the next AI that works event
            from baml_client.async_client import b

            # Prepare event data for BAML
            events_data = []
            for event in future_events[:10]:  # Limit to next 10 events
                events_data.append(
                    {
                        "event_id": event.event_id,
                        "title": event.title,
                        "description": event.description or "",
                        "start_date": event.start_at.isoformat(),
                        "url": event.url,
                    }
                )

            result = await b.IdentifyNextAIThatWorksEvent(
                events=events_data, current_date=now.isoformat()
            )

            # Find and return the identified event
            if result.event_id:
                for event in future_events:
                    if event.event_id == result.event_id:
                        logger.info(
                            f"Identified next AI that works event: {event.title} on {event.start_at}"
                        )
                        return event

            logger.warning("Could not identify next AI that works event")
            return None

        except Exception as e:
            logger.error(f"Error fetching next upcoming event: {e}")
            return None


# Global client instance
luma_client = LumaClient()
