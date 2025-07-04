import logging
import asyncio
from typing import Dict, Optional
from baml_wrapper import get_baml_client
from baml_client.types import VideoSummary, EmailDraft, TwitterThread, LinkedInPost

logger = logging.getLogger(__name__)


class AIGenerationError(Exception):
    """Custom exception for AI generation errors"""

    pass


class AIGenerator:
    def __init__(self):
        self.client = get_baml_client()

    async def summarize_video(
        self, transcript: str, title: Optional[str] = None
    ) -> VideoSummary:
        """
        Generate video summary from transcript using BAML
        Returns: VideoSummary with bullet points, topics, and takeaways
        """
        try:
            logger.info(
                f"Generating video summary for transcript of length {len(transcript)}"
            )

            # Use BAML to generate structured summary
            summary = await self.client.SummarizeVideo(
                transcript=transcript, title=title
            )

            logger.info(
                f"Generated summary with {len(summary.bullet_points)} bullet points"
            )
            return summary

        except Exception as e:
            logger.error(f"Failed to generate video summary: {e}")
            raise AIGenerationError(f"Video summarization failed: {e}")

    async def generate_email_draft(
        self,
        summary: VideoSummary,
        transcript: Optional[str] = None,
        video_title: Optional[str] = None,
    ) -> EmailDraft:
        """
        Generate professional email draft from video summary
        Returns: EmailDraft with subject, body, and call-to-action
        """
        try:
            logger.info("Generating email draft from video summary")


            # Use BAML to generate email content
            email_draft = await self.client.GenerateEmailDraft(
                summary=summary, transcript=transcript, video_title=video_title
            )

            result = await self.client.GenerateEmailStructure(summary=summary, structure=email_draft)

            logger.info(
                f"Generated email draft with subject: {email_draft.subject[:50]}..."
            )
            return result

        except Exception as e:
            logger.error(f"Failed to generate email draft: {e}")
            raise AIGenerationError(f"Email generation failed: {e}")

    async def generate_twitter_thread(
        self, summary: VideoSummary, video_title: Optional[str] = None
    ) -> TwitterThread:
        """
        Generate Twitter thread from video summary
        Returns: TwitterThread with tweets and hashtags
        """
        try:
            logger.info("Generating Twitter thread from video summary")

            # Use BAML to generate Twitter content
            twitter_thread = await self.client.GenerateTwitterThread(
                summary=summary, video_title=video_title
            )

            logger.info(
                f"Generated Twitter thread with {len(twitter_thread.tweets)} tweets"
            )
            return twitter_thread

        except Exception as e:
            logger.error(f"Failed to generate Twitter thread: {e}")
            raise AIGenerationError(f"Twitter thread generation failed: {e}")

    async def generate_linkedin_post(
        self, summary: VideoSummary, video_title: Optional[str] = None
    ) -> LinkedInPost:
        """
        Generate LinkedIn post from video summary
        Returns: LinkedInPost with content and hashtags
        """
        try:
            logger.info("Generating LinkedIn post from video summary")

            # Use BAML to generate LinkedIn content
            linkedin_post = await self.client.GenerateLinkedInPost(
                summary=summary, video_title=video_title
            )

            logger.info(
                f"Generated LinkedIn post with {len(linkedin_post.content)} characters"
            )
            return linkedin_post

        except Exception as e:
            logger.error(f"Failed to generate LinkedIn post: {e}")
            raise AIGenerationError(f"LinkedIn post generation failed: {e}")

    async def generate_all_content(
        self, transcript: str, video_title: Optional[str] = None
    ) -> Dict:
        """
        Generate all content types from a video transcript
        Returns: Dictionary with summary and all content drafts
        """
        try:
            logger.info("Starting complete AI content generation pipeline")

            # Step 1: Generate video summary
            summary = await self.summarize_video(transcript, video_title)

            # Step 2: Generate all content types in parallel
            email_task = self.generate_email_draft(summary, transcript, video_title)
            twitter_task = self.generate_twitter_thread(summary, video_title)
            linkedin_task = self.generate_linkedin_post(summary, video_title)

            # Wait for all content generation to complete
            email_draft, twitter_thread, linkedin_post = await asyncio.gather(
                email_task, twitter_task, linkedin_task
            )

            result = {
                "summary": {
                    "bullet_points": summary.bullet_points,
                    "key_topics": summary.key_topics,
                    "main_takeaways": summary.main_takeaways,
                },
                "email_draft": {
                    "subject": email_draft.subject,
                    "body": email_draft.body,
                    "call_to_action": email_draft.call_to_action,
                },
                "twitter_thread": {
                    "tweets": twitter_thread.tweets,
                    "hashtags": twitter_thread.hashtags,
                },
                "linkedin_post": {
                    "content": linkedin_post.content,
                    "hashtags": linkedin_post.hashtags,
                },
                "status": "completed",
            }

            logger.info("Complete AI content generation pipeline finished successfully")
            return result

        except Exception as e:
            logger.error(f"Complete AI content generation failed: {e}")
            raise AIGenerationError(f"AI content generation pipeline failed: {e}")


# Global instance
ai_generator = AIGenerator()


# Convenience functions for external use
async def summarize_video(transcript: str, title: Optional[str] = None) -> VideoSummary:
    """Generate video summary from transcript"""
    return await ai_generator.summarize_video(transcript, title)


async def generate_email_draft(
    summary: VideoSummary,
    transcript: Optional[str] = None,
    video_title: Optional[str] = None,
) -> EmailDraft:
    """Generate email draft from video summary"""
    return await ai_generator.generate_email_draft(summary, transcript, video_title)


async def generate_twitter_thread(
    summary: VideoSummary, video_title: Optional[str] = None
) -> TwitterThread:
    """Generate Twitter thread from video summary"""
    return await ai_generator.generate_twitter_thread(summary, video_title)


async def generate_linkedin_post(
    summary: VideoSummary, video_title: Optional[str] = None
) -> LinkedInPost:
    """Generate LinkedIn post from video summary"""
    return await ai_generator.generate_linkedin_post(summary, video_title)


async def generate_all_content(
    transcript: str, video_title: Optional[str] = None
) -> Dict:
    """Generate all content types from transcript"""
    return await ai_generator.generate_all_content(transcript, video_title)
