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
def get_episode_repo_path(...args...):
    """
    get the episode name somehow

    examples are 
    2025-04-15-code-generation-small-models      
    2025-06-10-cracking-the-prompting-interview
    2025-04-22-twelve-factor-agents              
    2025-06-17-entity-extraction
    2025-06-24-ai-content-pipeline
    2025-07-01-ai-content-pipeline-2
    2025-05-17-workshop-sf-twelve-factor-agents 
    2025-05-20-policies-to-prompts              
    """
    # todo we will need to figure out a smart way to implement this
    # is is LIKELY already pushed to the repo, so maybe supersonic can help us
    # or cased/kit can help us get the list of existing folders and we can
    # guess the rigth one with a baml ai function based on the video title
    # and zoom recording date



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
        next_episode_summary: str,
        next_episode_luma_link: str,
    ) -> str:
        """Create a PR with all generated content for an episode"""

        path = get_episode_repo_path(video_title, episode_date)

        # Format content for the PR
        episode_readme = self._generate_episode_readme(
            video_title=video_title,
            episode_date=episode_date,
            summary=summary,
            youtube_url=youtube_url,
            youtube_thumbnail_url=youtube_thumbnail_url,
        )

        root_readme = self._generate_root_readme(
            video_title=video_title,
            episode_date=episode_date,
            next_episode_summary=next_episode_summary,
            next_episode_luma_link=next_episode_luma_link,
        )
        
        # Create PR using Supersonic
        pr = self.supersonic.create_pr_from_multiple_contents(
            repo=f"{self.repo_owner}/{self.repo_name}",
            contents={
                f"{path}/README.md": episode_readme,
                f"README.md": root_readme,
            },
            title=f"[AUTO] content for {path}",
            description=f"Automated PR for content drafts for {path} episode: {video_title}",
            reviewers=["dexhorthy", "hellovai"]
        )
        
        return pr.html_url
    def _generate_episode_readme(self, ...args...):
        """
        generate the episode readme

        follows the prompts in .prompts/recap-and-next.md
        """
        pass

    def _generate_root_readme(
        self, ...args...
        ):
        """
        generate the root readme

        follows the prompts in .prompts/recap-and-next.md
        """
        pass
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

## Next Steps

1. Install Supersonic and kit dependencies
2. Prompt user to ensure github token is set in .env
3. Implement `github_pr_service.py`
4. Update main pipeline to integrate PR creation
5. Test with a sample video
6. Deploy to production