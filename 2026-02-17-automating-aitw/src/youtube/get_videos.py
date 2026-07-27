"""Find the most recent full-length episode recording on the channel."""

from src.youtube.youtube_client import YouTubeClient, Video
from dotenv import load_dotenv
load_dotenv()


# Full episodes run ~45-90 minutes. Clips and shorts are under a couple of minutes,
# so any comfortable threshold in between separates them cleanly.
MIN_EPISODE_SECONDS = 20 * 60

# How many recent uploads to scan. Clips are published far more often than
# episodes, so this needs enough headroom to reach past a week of clips.
SEARCH_DEPTH = 25


def _format_duration(seconds: int) -> str:
    """Render a duration as e.g. '55m23s'."""
    return f"{seconds // 60}m{seconds % 60:02d}s"


def get_episode_candidates(
    handle: str = "@boundaryml",
    max_results: int = SEARCH_DEPTH,
    min_seconds: int = MIN_EPISODE_SECONDS,
) -> list[Video]:
    """
    Get recent full-length videos from the channel, newest first.

    Episodes are identified by duration rather than by title. The channel used to
    tag episodes with '🦄 #<number>' but no longer does, and clips are titled the
    same way episodes are, so length is the only reliable signal.
    """
    client = YouTubeClient()
    videos = client.get_recent_videos_from_handle(handle, max_results=max_results)
    return [v for v in videos if v.duration_seconds >= min_seconds]


def main() -> dict[str, str]:
    """Get the most recently published full-length episode."""
    candidates = get_episode_candidates()
    if not candidates:
        return {}

    latest = candidates[0]
    return {latest.title: latest.url}


if __name__ == "__main__":
    candidates = get_episode_candidates()

    if not candidates:
        print(
            f"No video longer than {MIN_EPISODE_SECONDS // 60} minutes found in the "
            f"last {SEARCH_DEPTH} uploads. Pass the episode URL in manually."
        )
    else:
        latest = candidates[0]
        print(f"{latest.title}: {latest.url}")

        if len(candidates) > 1:
            print("\nOther recent full-length videos:")
            for video in candidates[1:5]:
                published = video.published_at.strftime("%Y-%m-%d")
                print(f"  [{published}, {_format_duration(video.duration_seconds)}] {video.title}: {video.url}")
