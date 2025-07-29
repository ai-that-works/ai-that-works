# Episode Prep Command

This command updates episode documentation after completing a live session.

## Overview
Update the just-completed episode README with YouTube link, thumbnail, and summary, update the main README with episode details, and add next episode info to the table.

## Steps

1. **Check current date** - Use bash to verify today's date
2. **Gather required information** - Ensure you have:
   - Next episode signup link (starting with lu.ma/...)
   - Summary/description of the next episode
   - YouTube link to the just-completed recording
   - Folder for the just-completed episode (dated today or yesterday) (use List() or Bash(ls) to check if it exists)


   **STOP and ask the user if ANY of these are missing**

3. **Request episode summary** - When all info is verified, ask the user for the summary of the just-completed episode

4. **Update main README.md**:
   - Add the YouTube link for the just-completed episode
   - Add link to code in the just-completed episode folder
   - Add next episode signup link and description at the top of the episodes table

5. **Update episode-specific README**:
   - Navigate to the just-completed episode folder
   - Read at least 3 other episode READMEs to understand the format
   - Update the README with the provided summary
   - **IMPORTANT**: Add YouTube thumbnail using this exact format (see 2025-07-08-context-engineering/README.md for example):
     ```markdown
     [![Episode Title](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
     ```
     Extract the VIDEO_ID from the YouTube URL (the part after v= or youtu.be/)
   - Leave whiteboards and links sections blank for manual addition

## Important Notes
- Use TodoWrite to track progress through these steps
- Think deeply about the structure and format before making changes
- Verify all information is present before proceeding with updates
- Maintain consistency with existing episode documentation format
- The YouTube thumbnail is REQUIRED - reference 2025-07-08-context-engineering/README.md as a working example
