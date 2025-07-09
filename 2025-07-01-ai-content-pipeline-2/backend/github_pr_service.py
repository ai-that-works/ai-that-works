from supersonic import Supersonic
import os
from datetime import datetime
from baml_client.async_client import b
from baml_client.types import VideoSummary, TimeData
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def get_episode_repo_path(
    video_title: str,
    episode_date: str,
    zoom_recording_date: datetime,
    repo_owner: str,
    repo_name: str,
    github_token: str = None,
) -> str:
    """
    Determine episode folder name using BAML to match against all existing folders.

    Examples of episode folder names:
    - 2025-04-15-code-generation-small-models
    - 2025-06-10-cracking-the-prompting-interview
    - 2025-04-22-twelve-factor-agents
    - 2025-06-17-entity-extraction
    - 2025-06-24-ai-content-pipeline
    - 2025-07-01-ai-content-pipeline-2
    - 2025-05-17-workshop-sf-twelve-factor-agents
    - 2025-05-20-policies-to-prompts
    """
    from kit import Repository

    # Get existing folders from repo using kit
    repo_url = f"https://github.com/{repo_owner}/{repo_name}"
    logger.debug(f"[get_episode_repo_path] Creating Repository instance for: {repo_url}")
    logger.debug(f"[get_episode_repo_path] Using github_token: {'***' + github_token[-4:] if github_token else 'None'}")
    
    try:
        repo = Repository(
            repo_url,
            github_token=github_token,
            ref='main'
        )
        logger.debug(f"[get_episode_repo_path] Repository instance created successfully")
        
        # Additional debug info
        logger.debug(f"[get_episode_repo_path] Repository attributes: owner={repo_owner}, name={repo_name}")
        
        logger.debug(f"[get_episode_repo_path] Getting file tree...")
        file_tree = repo.get_file_tree()
        logger.debug(f"[get_episode_repo_path] File tree retrieved with {len(file_tree)} entries")
        
        # If empty, try to understand why
        if len(file_tree) == 0:
            logger.warning(f"[get_episode_repo_path] File tree is empty! This might indicate:")
            logger.warning(f"[get_episode_repo_path] - Wrong repository URL: {repo_url}")
            logger.warning(f"[get_episode_repo_path] - Authentication issues with token")
            logger.warning(f"[get_episode_repo_path] - Repository is actually empty")
            logger.warning(f"[get_episode_repo_path] - Kit library issue")
    except Exception as e:
        logger.error(f"[get_episode_repo_path] Error creating repo or getting file tree: {type(e).__name__}: {str(e)}")
        raise

    # Get all episode folders (date-prefixed directories at root level)
    folders = [
        f["path"]
        for f in file_tree
        if f["is_dir"]
        and f["path"].count("/") == 0  # Root level only
        and re.match(r"\d{4}-\d{2}-\d{2}-", f["path"])
    ]
    logger.debug(f"[get_episode_repo_path] Found {len(folders)} episode folders: {folders[:5]}..." if len(folders) > 5 else f"[get_episode_repo_path] Found {len(folders)} episode folders: {folders}")

    # Use BAML to find best match or generate new name
    logger.debug(f"[get_episode_repo_path] Calling BAML DetermineEpisodePath with video_title='{video_title}', date={zoom_recording_date.isoformat()}")
    result = await b.DetermineEpisodePath(
        video_title=video_title,
        zoom_recording_date=zoom_recording_date.isoformat(),
        existing_folders=folders,
    )
    logger.debug(f"[get_episode_repo_path] BAML returned episode_path: '{result.episode_path}'")

    return result.episode_path


class GitHubPRService:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("missing or invalid parameters: GITHUB_TOKEN")

        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "hellovai")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "ai-that-works")
        self.supersonic = Supersonic(self.github_token)

    async def create_content_pr(
        self,
        video_id: str,
        video_title: str,
        episode_date: str,
        summary: dict,  # VideoSummary as dict from database
        youtube_url: str,
        youtube_thumbnail_url: str,
        transcript: str,
        zoom_recording_date: datetime,
        next_episode_summary: str,
        next_episode_luma_link: str,
    ) -> str:
        """Create a PR with all generated content for an episode"""
        logger.info(f"[create_content_pr] Starting PR creation for video_id: {video_id}, title: '{video_title}'")
        logger.debug(f"[create_content_pr] Params: episode_date={episode_date}, youtube_url={youtube_url}")

        # Determine the episode path
        logger.debug(f"[create_content_pr] Getting episode path...")
        try:
            episode_path = await get_episode_repo_path(
                video_title=video_title,
                episode_date=episode_date,
                zoom_recording_date=zoom_recording_date,
                repo_owner=self.repo_owner,
                repo_name=self.repo_name,
                github_token=self.github_token,
            )
            logger.info(f"[create_content_pr] Episode path determined: '{episode_path}'")
        except Exception as e:
            logger.error(f"[create_content_pr] Failed to get episode path: {type(e).__name__}: {str(e)}")
            raise

        # Generate content for the PR
        logger.debug(f"[create_content_pr] Generating episode README...")
        try:
            episode_readme = await self._generate_episode_readme(
                video_title=video_title,
                episode_date=episode_date,
                summary=summary,
                youtube_url=youtube_url,
                youtube_thumbnail_url=youtube_thumbnail_url,
                episode_path=episode_path,
            )
            logger.info(f"[create_content_pr] Episode README generated, length: {len(episode_readme)} chars")
        except Exception as e:
            logger.error(f"[create_content_pr] Failed to generate episode README: {type(e).__name__}: {str(e)}")
            raise

        logger.debug(f"[create_content_pr] Generating root README update...")
        try:
            root_readme = await self._generate_root_readme(
                video_title=video_title,
                episode_date=episode_date,
                episode_path=episode_path,
                next_episode_summary=next_episode_summary,
                next_episode_luma_link=next_episode_luma_link,
            )
            logger.info(f"[create_content_pr] Root README generated, length: {len(root_readme)} chars")
        except Exception as e:
            logger.error(f"[create_content_pr] Failed to generate root README: {type(e).__name__}: {str(e)}")
            raise

        # Determine branch name
        branch_name = f"content/{episode_path}"

        # Create PR description
        pr_description = f"""## Automated Content Update

This PR adds content for the episode: **{video_title}**

### Changes:
- ✅ Created/Updated episode README at `{episode_path}/README.md`
- ✅ Updated root README with completed episode and next session details

### Episode Details:
- **Date**: {episode_date}
- **YouTube**: {youtube_url}
- **Folder**: `{episode_path}`

### Next Session:
- **Summary**: {next_episode_summary}
- **Luma**: {next_episode_luma_link}

---
*This PR was automatically generated by the AI Content Pipeline*
"""

        # Create PR using Supersonic
        logger.info(f"[create_content_pr] Creating PR with branch: '{branch_name}'")
        logger.debug(f"[create_content_pr] PR files: {list(files.keys()) if 'files' in locals() else [f'{episode_path}/README.md', 'README.md']}")
        
        try:
            pr_url = await self.supersonic.create_pr_from_files(
                repo=f"{self.repo_owner}/{self.repo_name}",
                files={
                    f"{episode_path}/README.md": episode_readme,
                    "README.md": root_readme,
                },
                branch_name=branch_name,
                base_branch="main",
                title=f"[AUTO] Content for {episode_path}",
                body=pr_description,
                labels=["generated"],
                draft=False,
            )
            logger.info(f"[create_content_pr] PR created successfully: {pr_url}")
        except Exception as e:
            logger.error(f"[create_content_pr] Failed to create PR: {type(e).__name__}: {str(e)}")
            raise

        return pr_url

    async def _generate_episode_readme(
        self,
        video_title: str,
        episode_date: str,
        summary: dict,  # VideoSummary as dict from database
        youtube_url: str,
        youtube_thumbnail_url: str,
        episode_path: str,
    ) -> str:
        """Generate the episode README using BAML and the example template"""
        from kit import Repository

        # Convert dict summary to BAML VideoSummary type
        summary_obj = VideoSummary(
            bullet_points=summary.get("bullet_points", []),
            key_topics=summary.get("key_topics", []),
            main_takeaways=summary.get("main_takeaways", []),
            timed_data=[TimeData(**td) for td in summary.get("timed_data", [])]
            if summary.get("timed_data")
            else [],
        )

        # Check if README already exists
        existing_readme = None
        repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        logger.debug(f"[_generate_episode_readme] Checking for existing README at '{episode_path}/README.md'")
        
        try:
            logger.debug(f"[_generate_episode_readme] Creating Repository instance for: {repo_url}")
            repo = Repository(repo_url, ref='main')
            
            logger.debug(f"[_generate_episode_readme] Getting file content for: ['{episode_path}/README.md']")
            existing_content = repo.get_file_content([f"{episode_path}/README.md"])
            existing_readme = existing_content.get(f"{episode_path}/README.md")
            logger.info(f"[_generate_episode_readme] Found existing README, length: {len(existing_readme) if existing_readme else 0} chars")
        except Exception as e:
            logger.debug(f"[_generate_episode_readme] No existing README found or error: {type(e).__name__}: {str(e)}")
            # File doesn't exist yet
            pass

        # Generate the README using BAML
        episode_readme = await b.GenerateEpisodeReadme(
            video_title=video_title,
            episode_date=episode_date,
            summary=summary_obj,
            youtube_url=youtube_url,
            youtube_thumbnail_url=youtube_thumbnail_url,
            existing_readme_content=existing_readme,
        )

        return episode_readme

    async def _generate_root_readme(
        self,
        video_title: str,
        episode_date: str,
        episode_path: str,
        next_episode_summary: str,
        next_episode_luma_link: str,
    ) -> str:
        """Generate the updated root README"""
        from kit import Repository

        # Get current root README
        repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        logger.info(f"[_generate_root_readme] Getting current root README from: {repo_url}")
        logger.debug(f"[_generate_root_readme] Using github_token: {'***' + self.github_token[-4:] if self.github_token else 'None'}")
        
        try:
            logger.debug(f"[_generate_root_readme] Creating Repository instance...")
            repo = Repository(
                repo_url,
                github_token=self.github_token,
                ref='main'
            )
            logger.debug(f"[_generate_root_readme] Repository instance created successfully")
            
            # Debug: Check file tree to see what files exist
            logger.debug(f"[_generate_root_readme] Getting file tree to debug...")
            try:
                file_tree = repo.get_file_tree()
                root_files = [f for f in file_tree if f["path"].count("/") == 0]
                logger.debug(f"[_generate_root_readme] Root level files: {[f['path'] for f in root_files]}")
                readme_files = [f for f in file_tree if 'readme' in f["path"].lower()]
                logger.debug(f"[_generate_root_readme] All README files found: {[f['path'] for f in readme_files]}")
            except Exception as e:
                logger.error(f"[_generate_root_readme] Failed to get file tree: {type(e).__name__}: {str(e)}")
            
            logger.debug(f"[_generate_root_readme] Calling get_file_content(['README.md'])...")
            try:
                current_readme_dict = repo.get_file_content(["README.md"])
                logger.debug(f"[_generate_root_readme] get_file_content returned dict with keys: {list(current_readme_dict.keys())}")
                
                if "README.md" not in current_readme_dict:
                    logger.error(f"[_generate_root_readme] README.md not found in response dict. Keys: {list(current_readme_dict.keys())}")
                    raise KeyError("README.md not found in file content response")
                
                current_readme = current_readme_dict["README.md"]
                logger.info(f"[_generate_root_readme] Retrieved root README, length: {len(current_readme)} chars")
            except (OSError, IOError) as e:
                if "Files not found: README.md" in str(e):
                    logger.warning(f"[_generate_root_readme] Kit library failed to find README.md, trying alternative approach...")
                    # Try to get the file directly
                    try:
                        # Use a simpler approach - get the file content directly
                        current_readme_dict = repo.get_file_content("README.md")
                        if isinstance(current_readme_dict, dict) and "README.md" in current_readme_dict:
                            current_readme = current_readme_dict["README.md"]
                        elif isinstance(current_readme_dict, str):
                            current_readme = current_readme_dict
                        else:
                            raise ValueError(f"Unexpected response type: {type(current_readme_dict)}")
                        logger.info(f"[_generate_root_readme] Alternative approach succeeded, retrieved README, length: {len(current_readme)} chars")
                    except Exception as alt_e:
                        logger.error(f"[_generate_root_readme] Alternative approach also failed: {type(alt_e).__name__}: {str(alt_e)}")
                        # As a last resort, use a placeholder
                        logger.warning(f"[_generate_root_readme] Using empty README as fallback")
                        current_readme = ""
                else:
                    raise
        except Exception as e:
            logger.error(f"[_generate_root_readme] Failed to get root README: {type(e).__name__}: {str(e)}")
            logger.error(f"[_generate_root_readme] Full exception details:", exc_info=True)
            raise

        # Generate the updated README using BAML
        updated_readme = await b.GenerateRootReadmeUpdate(
            current_readme=current_readme,
            new_episode_title=video_title,
            new_episode_path=episode_path,
            new_episode_date=episode_date,
            next_episode_summary=next_episode_summary,
            next_episode_luma_link=next_episode_luma_link,
        )

        return updated_readme
