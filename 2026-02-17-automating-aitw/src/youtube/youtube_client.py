"""YouTube API client for fetching channel videos."""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import urllib.parse
import urllib.request
import json


def _parse_iso8601_duration(duration: str) -> int:
    """
    Convert an ISO 8601 duration (e.g. 'PT55M23S') to seconds.

    Returns 0 if the string can't be parsed.
    """
    match = re.fullmatch(r"P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration or "")
    if not match:
        return 0

    days, hours, minutes, seconds = (int(g) if g else 0 for g in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


@dataclass
class Video:
    """Represents a YouTube video."""

    title: str
    video_id: str
    published_at: datetime
    description: str
    thumbnail_url: str
    duration_seconds: int = 0

    @property
    def url(self) -> str:
        """Returns the full YouTube URL for the video."""
        return f"https://www.youtube.com/watch?v={self.video_id}"


class YouTubeClient:
    """Client for interacting with the YouTube Data API v3."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube client.

        Args:
            api_key: YouTube Data API key. If not provided, reads from YOUTUBE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable or pass api_key parameter.")

        self.base_url = "https://www.googleapis.com/youtube/v3"

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """
        Make a request to the YouTube API.

        Args:
            endpoint: API endpoint (e.g., 'channels', 'search')
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        params["key"] = self.api_key
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/{endpoint}?{query_string}"

        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())

    def get_channel_id_from_handle(self, handle: str) -> str:
        """
        Get channel ID from a channel handle (e.g., '@boundaryml').

        Args:
            handle: Channel handle with @ prefix

        Returns:
            Channel ID
        """
        # Remove @ if present
        if handle.startswith("@"):
            handle = handle[1:]

        params = {
            "part": "id",
            "forHandle": handle
        }

        response = self._make_request("channels", params)

        if not response.get("items"):
            raise ValueError(f"Channel not found for handle: @{handle}")

        return response["items"][0]["id"]

    def get_recent_videos(self, channel_id: str, max_results: int = 3) -> List[Video]:
        """
        Get the most recent videos from a channel.

        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve (default: 3)

        Returns:
            List of Video objects, sorted by publish date (newest first)
        """
        # Search for videos from the channel
        search_params = {
            "part": "id",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": max_results
        }

        search_response = self._make_request("search", search_params)

        if not search_response.get("items"):
            return []

        # Get video IDs
        video_ids = [item["id"]["videoId"] for item in search_response["items"]]

        # Get video details
        video_params = {
            "part": "snippet,contentDetails",
            "id": ",".join(video_ids)
        }

        videos_response = self._make_request("videos", video_params)

        # Parse videos
        videos = []
        for item in videos_response.get("items", []):
            snippet = item["snippet"]
            video = Video(
                title=snippet["title"],
                video_id=item["id"],
                published_at=datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")),
                description=snippet["description"],
                thumbnail_url=snippet["thumbnails"]["high"]["url"],
                duration_seconds=_parse_iso8601_duration(item.get("contentDetails", {}).get("duration", "")),
            )
            videos.append(video)

        # The videos endpoint doesn't preserve the search order, so re-sort
        videos.sort(key=lambda v: v.published_at, reverse=True)

        return videos

    def get_recent_videos_from_handle(self, handle: str, max_results: int = 3) -> List[Video]:
        """
        Get the most recent videos from a channel using its handle.

        Args:
            handle: Channel handle (e.g., '@boundaryml' or 'boundaryml')
            max_results: Maximum number of videos to retrieve (default: 3)

        Returns:
            List of Video objects, sorted by publish date (newest first)
        """
        channel_id = self.get_channel_id_from_handle(handle)
        return self.get_recent_videos(channel_id, max_results)
