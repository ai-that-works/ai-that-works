---
name: episode_prep
description: prepare an episode
---

# Episode Prep Command

This command prepares the documentation for an upcoming episode.

## Overview
Add next episode info to the table in the main README.md.

## Steps

1. **Check current date** - Use bash to verify today's date, run `bash(ls .)` to see the top level of folder structure here

2. **Get needed information from the user**
Ask the user for the following:
* Episode title
* Episode description
* Episode number
* Episode date
* Luma URL suffix
* Any additional guests to invite to the Riverside event
**STOP and ask the user UNTIL YOU HAVE ALL OF THESE DATA POINTS**

3. **Generate the image for the event**
Use the provided information to run the cli:
```bash
   cd 2026-02-17-automating-aitw
   uv run python -m src.thumbnail_creation.cli --title <provided episode title> --description <provided description> --episode-number <provided episode number>
```
This will generate an outputted image and subtitle. Give the user:
- The generated subtitle
- The path to the outputted `.png`

Ask the user if they are satisfied with the result. If not, ask them what they don't like about it. Then run:
```bash
   cd 2026-02-17-automating-aitw
   uv run python -m src.thumbnail_creation.cli --title <provided episode title> --description <provided description> --episode-number <provided episode number> --current-subtitle <the subtitle that was just generated> --feedback <the user's feedback>
```
The system will automatically categorize the feedback as relating to the subtitle, the image, or both, and regenerate accordingly. Keep repeating this feedback loop until the user is satisfied with the image.

4. **Update the provided description**
   - If the provided episode description does not end with "Meet the Speakers🧑‍💻​

   ​​Meet Vaibhav Gupta, one of the creators of BAML and YC alum. He spent 10 years in AI performance optimization at places like Google, Microsoft, and D. E. Shaw. He loves diving deep and chatting about anything related to Gen AI and Computer Vision!

   ​Meet Dex Horthy, founder at HumanLayer and coiner of the term Context Engineering. He spent 10+ years building devops tools at Replicated, Sprout Social and JPL. DevOps junkie turned AI Engineer.", append that to the description and use that as the new episode description going forward

5. **Create  the event in Riverside**
Run this script:
```bash
   cd 2026-02-17-automating-aitw
   uv run python -m src.riverside.cli --title <provided episode title> --description <provided description> --episode-number <provided episode number> --date <provided date> --guests <additional guests if any. if none, do not add this argument>
```
This will create the riverside event.

6. **STOP. Tell the user to finish the Riverside Event**
Tell the user to go turn on the livestreams and upload the generated image in Riverside. STOP AND WAIT until the user has indicated that they have done this. Once they say they have, continue.

7. **Create the Luma Event**
   - If the provided episode title does not start with "🦄 ai that works: ", prepend that to the episode title and use that as the new episode title going forward.
   - Navigate to the `2026-02-17-automating-aitw` directory and run the script
   ```bash
   uv run python -m src.luma.cli --name <episode title prepended by 🦄 ai that works:> --description <provided episode description appended with the Meet the Speakers...> --date <episode date> --cover-image-path <absolute path to outputted image from step 3> --luma-url-suffix <provided luma url suffix>
   ```

8. **Create new episode meta.md**
   - Read at least 3 other past episode meta.mds to understand the format
   - Create a new folder for the upcoming episode following the format
   - Create a meta.md, set the youtube link to `https://www.youtube.com/playlist?list=PLi60mUelRAbFqfgymVfZttlkIyt0XHZjt`, set the code url to `https://github.com/ai-that-works/ai-that-works`
   - Update the luma links


```example initial meta.md
---
guid: aitw-EPISODENUMBER
title: ".."
description: |
  ..
event_link: https://luma.com/<something>
eventDate: YYYY-MM-DDT18:00:00Z
media:
  url: https://www.youtube.com/playlist?list=PLi60mUelRAbFqfgymVfZttlkIyt0XHZjt
  type: video/youtube
links:
  code: https://github.com/ai-that-works/ai-that-works/tree/main/YYYY-MM-DD-<folder-name>
  # no youtube link here yet
season: 2
episode: EPISODENUMBER
event_type: episode
---
```

9. **Run the tools to regenerate the JSON manifest**
   - cd tools && bun run readme

## Important Notes
- Use TodoWrite to track progress through these steps
- Think deeply about the structure and format before making changes
- Verify all information is present before proceeding with updates
- Maintain consistency with existing episode documentation format
- The YouTube thumbnail is REQUIRED - reference 2025-07-08-context-engineering/README.md as a working example
