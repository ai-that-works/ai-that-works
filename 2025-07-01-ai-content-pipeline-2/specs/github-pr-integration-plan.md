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

## Manual GitHub PR Creation Flow

### UI Integration

The GitHub PR creation will be triggered manually from the UI, not automatically as part of the pipeline.

#### Summary Section UI Updates

In the video summary section, add a "Create GitHub Draft" button that:
- Only appears when all required data is available:
  - YouTube URL exists
  - Transcript is generated
  - Summary is complete
  - Next episode details are provided (summary + Luma link)
- Is disabled with tooltip explaining what's missing if any required data is unavailable
- Shows loading state while PR is being created
- Shows success/error state after creation attempt

#### Updated Flow

1. User completes video processing (Zoom → YouTube → Transcript → Summary)
2. User provides next episode details in the UI
    - next luma link
    - next episode summary
3. User clicks "Create GitHub Draft" button
4. System creates PR with:
   - Episode README in appropriate folder
   - Updated root README with episode moved to "Past Sessions"
   - Next session details updated
5. System shows PR URL in UI for review


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


#### 3. API Endpoint for Manual Trigger

Add to `backend/main.py`:

```python
@app.post("/api/videos/{video_id}/create-github-pr")
async def create_github_pr(
    video_id: str,
    request: CreateGitHubPRRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger GitHub PR creation for a video"""

    # Validate video exists and has required data
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Check required fields
    if not video.youtube_url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")
    if not video.transcript:
        raise HTTPException(status_code=400, detail="Transcript is required")
    if not video.summary:
        raise HTTPException(status_code=400, detail="Summary is required")

    # Validate request has next episode details
    if not request.next_episode_summary or not request.next_episode_luma_link:
        raise HTTPException(status_code=400, detail="Next episode details are required")

    try:
        # Initialize GitHub service
        github_service = GitHubPRService()

        # Create PR
        pr_url = await github_service.create_content_pr(
            video_id=video.id,
            video_title=video.title,
            episode_date=video.recording_date.strftime("%Y-%m-%d"),
            summary=video.summary,
            youtube_url=video.youtube_url,
            youtube_thumbnail_url=f"https://img.youtube.com/vi/{video.youtube_video_id}/0.jpg",
            transcript=video.transcript,
            zoom_recording_date=video.recording_date,
            next_episode_summary=request.next_episode_summary,
            next_episode_luma_link=request.next_episode_luma_link,
        )

        # Update video with PR URL
        video.github_pr_url = pr_url
        video.episode_path = await github_service.get_episode_path(video)
        db.commit()

        return {
            "pr_url": pr_url,
            "episode_path": video.episode_path,
            "message": "GitHub PR created successfully"
        }

    except Exception as e:
        logger.error(f"Failed to create GitHub PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Request model
class CreateGitHubPRRequest(BaseModel):
    next_episode_summary: str
    next_episode_luma_link: str
```

#### 4. UI Component Implementation

Add to `frontend/src/components/VideoSummary.tsx`:

```typescript
interface CreateGitHubPRButtonProps {
  video: Video;
  onSuccess: (prUrl: string) => void;
}

export function CreateGitHubPRButton({ video, onSuccess }: CreateGitHubPRButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [nextEpisodeSummary, setNextEpisodeSummary] = useState("");
  const [nextEpisodeLumaLink, setNextEpisodeLumaLink] = useState("");
  const [showForm, setShowForm] = useState(false);

  // Check if all required data is available
  const canCreatePR = video.youtube_url && video.transcript && video.summary;

  const missingItems = [];
  if (!video.youtube_url) missingItems.push("YouTube URL");
  if (!video.transcript) missingItems.push("Transcript");
  if (!video.summary) missingItems.push("Summary");

  const handleCreatePR = async () => {
    if (!nextEpisodeSummary || !nextEpisodeLumaLink) {
      toast.error("Please provide next episode details");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/videos/${video.id}/create-github-pr`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify({
          next_episode_summary: nextEpisodeSummary,
          next_episode_luma_link: nextEpisodeLumaLink
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create PR');
      }

      const data = await response.json();
      toast.success('GitHub PR created successfully!');
      onSuccess(data.pr_url);
      setShowForm(false);
    } catch (error) {
      toast.error(error.message || 'Failed to create GitHub PR');
    } finally {
      setIsLoading(false);
    }
  };

  if (!canCreatePR) {
    return (
      <Tooltip content={`Missing: ${missingItems.join(', ')}`}>
        <Button disabled variant="outline">
          <GitHubIcon className="mr-2 h-4 w-4" />
          Create GitHub Draft
        </Button>
      </Tooltip>
    );
  }

  return (
    <>
      <Button
        onClick={() => setShowForm(true)}
        variant="outline"
        disabled={video.github_pr_url !== null}
      >
        <GitHubIcon className="mr-2 h-4 w-4" />
        {video.github_pr_url ? 'PR Created' : 'Create GitHub Draft'}
      </Button>

      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create GitHub PR</DialogTitle>
            <DialogDescription>
              Provide details for the next episode to update the repository
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="next-summary">Next Episode Summary</Label>
              <Textarea
                id="next-summary"
                value={nextEpisodeSummary}
                onChange={(e) => setNextEpisodeSummary(e.target.value)}
                placeholder="Brief description of the next episode..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="luma-link">Next Episode Luma Link</Label>
              <Input
                id="luma-link"
                type="url"
                value={nextEpisodeLumaLink}
                onChange={(e) => setNextEpisodeLumaLink(e.target.value)}
                placeholder="https://lu.ma/..."
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleCreatePR}
              disabled={isLoading || !nextEpisodeSummary || !nextEpisodeLumaLink}
            >
              {isLoading ? 'Creating...' : 'Create PR'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
```

#### 5. Environment Variables

Add to `.env.template`:

```bash
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO_OWNER=dexhorthy
GITHUB_REPO_NAME=ai-that-works
```

#### 6. Database Schema Update

Add migration to track GitHub PR information:

```sql
-- migrations/add_github_pr_fields.sql
ALTER TABLE videos ADD COLUMN github_pr_url TEXT;
ALTER TABLE videos ADD COLUMN episode_path TEXT;
ALTER TABLE videos ADD COLUMN github_pr_created_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN github_pr_created_by TEXT;
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

## Summary

This implementation provides a manual GitHub PR creation flow that:

1. **User Control**: PR creation is triggered manually via UI button, not automatically
2. **Validation**: Button is disabled until all required data is available (YouTube URL, transcript, summary)
3. **Next Episode Input**: User provides next episode details through a dialog form
4. **PR Creation**: Creates a single PR with:
   - New/updated episode README in the correct folder
   - Updated root README with episode moved to past sessions and next session details
5. **Feedback**: Shows PR URL in UI for review

## Next Steps

1. Install dependencies: `uv add supersonic kit`
2. Add GITHUB_TOKEN to .env (personal access token with repo write permissions)
3. Implement `backend/github_pr_service.py` with the GitHubPRService class
4. Add the API endpoint to `backend/main.py`
5. Update frontend VideoSummary component to include CreateGitHubPRButton
6. Run database migration to add github_pr fields
7. Test with a sample video
