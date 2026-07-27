# Find Clips Command

This command runs a CLI that finds clippable content after completing a live session.

## Overview
Find the relevant directory and run the clip extractor CLI.

## Steps
1. **Check current date** - Use bash to verify today's date, run `bash(ls .)` to see the top level of folder structure here

1. **Get the Folder for the Just Completed Episode**
   -  Each episode has a folder in the repo with the date followed by the title (e.g., `YYYY-MM-DD-kebab-case-episode-title`)
   - Ask the user to choose from the most recent 5 episode folders *that are not in the future*. 
   - Give the user an option to provide their own if they do not want to select one of the options presented, but ensure it exists in the repo.

2. **Verify the Directory**
Make sure there is a `transcript.txt` and a `meta.md` in the directory. If there isn't, ask the user for them.

3. **Gather the Required Information from the meda.md**
Gather the following information from the `meta.md`.
    - episode title
    - description

4. **Run the extract clip cli**
Run the following script:
```bash
cd 2026-02-17-automating-aitw
uv run python -m src.clip_extractor.cli --transcript <path to transcript> --title <episode title> --description <episode description> --output <path to episode's directory>
```

## Important Notes
- Use TodoWrite to track progress through these steps
- Think deeply about the structure and format before making changes
- Verify all information is present before proceeding with updates