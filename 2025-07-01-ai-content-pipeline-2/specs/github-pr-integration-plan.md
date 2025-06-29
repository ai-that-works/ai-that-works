# GitHub PR Integration Plan for AI Content Pipeline

## Overview

This plan outlines the integration of GitHub PR creation into the AI Content Pipeline using Cased Supersonic. The goal is to automatically create a PR with the generated content (email, Twitter/X, LinkedIn drafts) as part of the content generation pipeline.

## Current Pipeline Architecture

The current pipeline flow:
1. Import video from Zoom
2. Upload to YouTube
3. Generate transcript
4. Generate summary
5. Generate content drafts in parallel:
   - Email draft
   - Twitter/X thread
   - LinkedIn post
6. Store drafts in database

## adding content publishing to the pipeline

Updated pipeline flow: 
1. Import video from Zoom
2. Upload to YouTube
3. Generate transcript
4. Generate summary
5. Generate content drafts in parallel:
   - Email draft
   - Twitter/X thread
   - LinkedIn post
   - GitHub Episode Readme
   - GitHub Root Readme
6. Store drafts in database
7. on human approval via UI, execute drafts:
   - email -> send to loops API as new campaign draft
   - Twitter -> no action, will post manually
   - LinkedIn -> no action, will post manually
   - github changes: push to github as new PR


### Implementation Details

#### 1. Add Supersonic Dependency

```bash
uv add supersonic
```

#### 2. Create GitHub PR Service

Create a new file `backend/github_pr_service.py`:

```python
from supersonic import Supersonic
import os
from typing import Dict, Any
from models import VideoSummary, EmailDraftContent, XDraftContent, LinkedInDraftContent

# we will need to figure out a smart way to get these
async def get_episode_repo_path(
    video_title: str, 
    episode_date: str, 
    zoom_recording_date: datetime,
    repo_owner: str,
    repo_name: str
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
    import re
    
    # Get existing folders from repo using kit
    repo = Repository(f"https://github.com/{repo_owner}/{repo_name}")
    file_tree = repo.get_file_tree()
    
    # Get all episode folders (date-prefixed directories at root level)
    folders = [
        f["path"] for f in file_tree 
        if f["is_dir"] 
        and f["path"].count("/") == 0  # Root level only
        and re.match(r'\d{4}-\d{2}-\d{2}-', f["path"])
    ]
    
    # Use BAML to find best match or generate new name
    result = await b.DetermineEpisodePath(
        video_title=video_title,
        zoom_recording_date=zoom_recording_date.isoformat(),
        existing_folders=folders
    )
    
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
        summary: VideoSummary,
        youtube_url: str,
        youtube_thumbnail_url: str,
        transcript: str,
        zoom_recording_date: datetime,
        next_episode_summary: str,
        next_episode_luma_link: str,
    ) -> str:
        """Create a PR with all generated content for an episode"""
        
        # Determine the episode path
        episode_path = await get_episode_repo_path(
            video_title=video_title,
            episode_date=episode_date,
            zoom_recording_date=zoom_recording_date,
            repo_owner=self.repo_owner,
            repo_name=self.repo_name
        )

        # Generate content for the PR
        episode_readme = await self._generate_episode_readme(
            video_title=video_title,
            episode_date=episode_date,
            summary=summary,
            youtube_url=youtube_url,
            youtube_thumbnail_url=youtube_thumbnail_url,
            transcript=transcript,
            episode_path=episode_path,
        )

        root_readme = await self._generate_root_readme(
            video_title=video_title,
            episode_date=episode_date,
            episode_path=episode_path,
            next_episode_summary=next_episode_summary,
            next_episode_luma_link=next_episode_luma_link,
        )
        
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
        pr = self.supersonic.create_pr_from_multiple_contents(
            repo=f"{self.repo_owner}/{self.repo_name}",
            contents={
                f"{episode_path}/README.md": episode_readme,
                "README.md": root_readme,
            },
            branch=branch_name,
            base_branch="main",
            title=f"[AUTO] Content for {episode_path}",
            description=pr_description,
            reviewers=["dexhorthy", "sxlijin"],
            labels=["auto-generated", "content"],
            draft=False
        )
        
        return pr.html_url
    async def _generate_episode_readme(
        self,
        video_title: str,
        episode_date: str,
        summary: VideoSummary,
        youtube_url: str,
        youtube_thumbnail_url: str,
        transcript: str,
        episode_path: str,
    ) -> str:
        """Generate the episode README using BAML and the example template"""
        from kit import Repository
        
        # Get the example readme template from BAML
        example_readme = ExampleEpisodeReadme()
        
        # Check if README already exists
        existing_readme = None
        try:
            repo = Repository(f"https://github.com/{self.repo_owner}/{self.repo_name}")
            existing_content = repo.get_file_content([f"{episode_path}/README.md"])
            existing_readme = existing_content.get(f"{episode_path}/README.md")
        except:
            # File doesn't exist yet
            pass
        
        # Generate the README using BAML
        episode_readme = await b.GenerateEpisodeReadme(
            video_title=video_title,
            episode_date=episode_date,
            summary=summary,
            youtube_url=youtube_url,
            youtube_thumbnail_url=youtube_thumbnail_url,
            transcript=transcript,
            example_readme=example_readme,
            existing_readme_content=existing_readme
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
        repo = Repository(f"https://github.com/{self.repo_owner}/{self.repo_name}")
        current_readme_dict = repo.get_file_content(["README.md"])
        current_readme = current_readme_dict["README.md"]
        
        # Generate the updated README using BAML
        updated_readme = await b.GenerateRootReadmeUpdate(
            current_readme=current_readme,
            new_episode_title=video_title,
            new_episode_path=episode_path,
            new_episode_date=episode_date,
            next_episode_summary=next_episode_summary,
            next_episode_luma_link=next_episode_luma_link
        )
        
        return updated_readme
```

as noted, read .prompts/recap-and-next.md for the prompts that will be used to make the BAML functions to generate these two files. you will likely need to pass in additional files to those prompts - you can use cased/kit to get the files and contents. Here is an end to end example:

```python
from kit import Repository

repo = Repository("https://github.com/owner/repo")

# Explore the repo
print(repo.get_file_tree())
# Output: [{"path": "src/main.py", "is_dir": False, ...}, ...]

# Read many files in one round-trip
contents = repo.get_file_content([
    "README.md",
])
print(contents["README.md"])
```


The example episode readme to pass in as part of the prompt is below. It must be passed in verbatim to the baml prompt, it should be written into a .baml file inside a function, or a template_string:

```baml
template_string ExampleEpisodeReadme() #"
... content ...
"#
```


<example_episode_readme>
# TITLE

> short description

[Video](URL) (1h15m) 

[![title](THUMBNAIL_URL)](URL)

Links:

- ...

## Key Takeaways

- ...

## Whiteboards

(intentionally blank)

## Core Architecture

...

## Running the Code

...

## Resources

- [Session Recording](YOUTUBE_URL)
- [BAML Documentation](https://docs.boundaryml.com/)
- [Discord Community](https://www.boundaryml.com/discord)
- Sign up for the next session on [Luma](NEXT_SESSION_URL)

</example_episode_readme>


#### 3. Integration with Main Pipeline

#### 4. Environment Variables

Add to `.env.template`:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO_OWNER=dexhorthy
GITHUB_REPO_NAME=ai-that-works
```

#### 5. Database Schema Update

Add migration to track PR URLs:

```sql
-- migrations/add_github_pr_url.sql
ALTER TABLE videos ADD COLUMN github_pr_url TEXT;
```

### BAML Function Definitions

Add these BAML functions to `backend/baml_src/content_generation.baml`:

```baml
class EpisodePathResult {
    episode_path: string
    is_new: bool
}

function DetermineEpisodePath(
    video_title: string, 
    zoom_recording_date: string,
    existing_folders: string[]
) -> EpisodePathResult {
    client CustomSonnet
    prompt #"
        Given a video title, recording date, and list of existing episode folders, 
        either find the matching folder or generate a new folder name.
        
        Video Title: {{video_title}}
        Recording Date: {{zoom_recording_date}}
        
        Existing Episode Folders:
        {{#each existing_folders}}
        - {{this}}
        {{/each}}
        
        Rules:
        1. If an existing folder matches the recording date exactly, return it
        2. If the video title strongly matches an existing folder topic, return it
        3. Otherwise, generate a new folder name in format: YYYY-MM-DD-kebab-case-title
        4. Remove generic words like "ai-that-works", "episode", "session" from the slug
        5. Keep the slug concise but descriptive
        
        Return the episode_path and whether it's new or existing.
    "#
}

function GenerateEpisodeReadme(
    video_title: string,
    episode_date: string,
    summary: VideoSummary,
    youtube_url: string,
    youtube_thumbnail_url: string,
    example_readme: string,
    existing_readme_content: string?
) -> string {
    client CustomSonnet
    prompt #"
        Generate an episode README following the exact format of the example.
        
        {{#if existing_readme_content}}
        Current README content to update:
        {{existing_readme_content}}
        {{/if}}
        
        Episode Details:
        - Title: {{video_title}}
        - Date: {{episode_date}}
        - YouTube URL: {{youtube_url}}
        - Thumbnail: {{youtube_thumbnail_url}}
        
        Summary:
        {{summary}}
        
        Example README format to follow EXACTLY:
        {{example_readme}}
        
        Instructions:
        - Follow the example structure precisely
        - Write a clear "Core Architecture" section based on technical content
        - Leave "Whiteboards" section as "(intentionally blank)"
        - Use the exact Resources section format with all links
    "#
}

function GenerateRootReadmeUpdate(
    current_readme: string,
    new_episode_title: string,
    new_episode_path: string,
    new_episode_date: string,
    next_episode_summary: string,
    next_episode_luma_link: string
) -> string {
    client "claude-3-5-sonnet-20241022"
    prompt #"
        Update the root README.md following these steps:
        
        1. Move the current "Next Session" content to the "Past Sessions" section
        2. Add the new completed episode to "Past Sessions" with proper formatting
        3. Update the "Next Session" section with the new upcoming session details
        
        Current README:
        {{current_readme}}
        
        Completed Episode to Add:
        - Title: {{new_episode_title}}
        - Path: {{new_episode_path}}
        - Date: {{new_episode_date}}
        
        Next Session Details:
        - Summary: 
        - Luma Link: {{next_episode_luma_link}}
        
        IMPORTANT:
        - Maintain the EXACT formatting and structure of the current README
        - Preserve all existing content except for the specific updates
        - Keep the same section headers and formatting style
        - Add the new episode entry in chronological order
    "#
}

template_string ExampleEpisodeReadme() #"
# TITLE

> short description

[Video](URL) (1h15m) 

[![title](THUMBNAIL_URL)](URL)

Links:

- ...

## Key Takeaways

- GraphQL provides a flexible query language that pairs well with LLM-based resolvers
- BAML's type safety ensures consistent API responses even with dynamic AI generation
- Streaming responses can significantly improve perceived performance for complex queries
- Proper error handling and fallbacks are crucial for production AI-powered APIs

## Whiteboards

(intentionally blank)

## Core Architecture

...

## Running the Code

...

...

## Resources

- [Session Recording](YOUTUBE_URL)
- [BAML Documentation](https://docs.boundaryml.com/)
- [Discord Community](https://www.boundaryml.com/discord)
- Sign up for the next session on [Luma](NEXT_SESSION_URL)
"#
```

## Next Steps

1. Install Supersonic and kit dependencies
2. Prompt user to ensure github token is set in .env
3. Implement `github_pr_service.py`
4. Update main pipeline to integrate PR creation
5. Test with a sample video
6. Deploy to production