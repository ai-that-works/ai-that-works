# Complete Episode Command

This command updates episode documentation and writes an email after completing a live session.

## Overview
Update the just-completed episode README and meta.md with YouTube link, thumbnail, and summary and update the main README with episode details. Then write an email.md file for the episode. Finally, back-fill the episode README's `## Key Takeaways` section from the finished email so the two stay in sync.

## Steps

1. **Check current date** - Use bash to verify today's date, run `bash(ls .)` to see the top level of folder structure here

2. **Get the Youtube Link for the just-completed recording**
   - Run the script: 
   ```bash
   cd 2026-02-17-automating-aitw
   uv run python -m src.youtube.get_videos
   ```
   - The script prints the most recently published full-length video (format: "title: url"), followed by a few older full-length videos as alternates. Episodes are detected by duration (20+ minutes), since clips are titled the same way episodes are.
   - Parse the output to extract the title and URL
   - Display the video title and link to the user in a clear format
   - Ask the user: "Is this the correct podcast recording video? (yes/no)"
   - If yes: save that URL and description to use for the rest of the command
   - If no: offer the listed alternates, or ask the user to provide the correct YouTube URL and the episode description manually and use them instead

3. **Get the Folder for the Just Completed Episode**
   - Each episode has a folder in the repo with the date followed by the title (e.g., `YYYY-MM-DD-kebab-case-episode-title`)
   - Ask the user to choose from the most recent 5. 
   - Give the user an option to provide their own if they do not want to select one of the options presented, but ensure it exists in the repo.

**STOP and ask the user UNTIL YOU HAVE ALL OF THESE DATA POINTS**

3. **Update completed episode meta.md**:
   - Read at least 3 other past episode meta.mds to understand the format
   - update the github link and youtube urls

4. **Update episode-specific README**:
   - Read `2025-07-08-context-engineering/README.md` for example
   - **IMPORTANT**: Add YouTube thumbnail using this exact format (see ):
     ```markdown
     [![Episode Title](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
     ```
     Extract the VIDEO_ID from the YouTube URL (the part after v= or youtu.be/)
   - Leave links sections blank for manual addition
   - Navigate to the just-completed episode folder
   - Update the README with the provided summary

4b. **Capture Whiteboards**:
   - Get the episode date from `meta.md` (the `eventDate` field, formatted as `YYYY-MM-DD`)
   - Run:
     ```bash
     cd 2026-02-17-automating-aitw
     uv run python -m src.excalidraw.browser_agent --date <YYYY-MM-DD> --output <abs_path_to_episode_folder>
     ```
   - If **successful** (exit code 0):
     - Parse the `BOARD_URL: <url>` line from stdout
     - Add the URL to `meta.md` under a `whiteboards:` YAML list field
     - Replace the `## Whiteboards` section in the README with:
       ```markdown
       ## Whiteboards

       [![Whiteboard 1](./whiteboard-1.png)](<BOARD_URL>)
       ```
   - If the script exits with **"Session expired or not logged in"** error:
     - Tell the user: "Run this to log in, then I'll retry: `cd 2026-02-17-automating-aitw && uv run python -m src.excalidraw.browser_agent --login`"
     - After they confirm, re-run the browser agent command above
   - If the script exits with **"No board found"** error:
     - Leave `## Whiteboards` blank and note it for the user to fill manually

5. **Run the tools to regenerate the JSON manifest**
   - cd tools && bun run readme

6. **Get the Required Information**
   - Get the episode title from the `meta.md` in the directory
   - Get the episode description from the `meta.md` in the directory

**STOP make sure you have the above information before continuing. If you are missing any of them, ask the user for them.**

7. **Verify the Transcript**
Make sure there is a `transcript.txt` file in the directory. If there isn't, ask the user for the transcript.

8. **Generate the Email JSON**
Use the provided information to run the cli:
```bash
   cd 2026-02-17-automating-aitw
   uv run python -m src.email_generator.generate_email --title <provided episode title> --description <provided description> --transcript <path to transcript> --output <path to episode directory>
```

9. **Convert to a email.md**
Convert the outputted json to an `email.md`

10. **Read Context**
   - List all email.md files: `*/email.md`
   - Read at least 3 recent email.md files to understand the tone, structure, and style
   - Read the README.md from the target episode directory to understand the content

11. **Analyze Email Structure**
Emails typically follow this format:
- **Greeting**: "Hello First Name,"
- **Opening**: Reference to "This week's 🦄 ai that works session" with the topic
- **Links**: GitHub repo link and YouTube video link
- **Key Takeaways**: 3-5 numbered or bulleted actionable insights
- **Memorable Quote**: "If you remember one thing from this session:" or "key takeaway" or something similar as a section
- **Next Session**: Information about tomorrow's session with Luma link (this email gets sent out the day before another session)
- **Call to Action**: Discord link, questions invitation
- **Sign-off**: "Happy coding 🧑‍💻" followed by "Vaibhav & Dex" or similar

12. **Humanize the Email**
These emails often sound like AI slop. Rewrite the email applying the following rules to make it sound more human-like:

   1. **Ban em-dashes entirely.** Do not use — anywhere in the email. Not once. If you find yourself wanting to use an em-dash, rewrite the sentence instead. Split it into two sentences, use a comma, use a colon, or restructure it. Em-dashes are the single clearest signal that an AI wrote something. Before finalizing, do a literal search for "—" and rewrite every instance.

   2. **Remove "It's not X, it's Y" constructions.** These sound like debate club. Just say the thing directly.

   3. **Vary sentence length.** Short sentences land harder. Long sentences are fine when you need to explain something with nuance, but don't make every sentence the same length or it starts to feel like a robot found a cadence and got stuck in it.

   4. **Replace abstract concepts with concrete examples.** Push every takeaway to include a specific "for example" moment that readers can immediately picture. Example before: "Email agents must handle cancellations, corrections, and race conditions." Example after: "when a user sends a follow-up saying 'actually no, I have an onsite' five seconds after their first email, the system needs to handle that gracefully."

   5. **Convert descriptions into actionable implications.** Don't just explain what something is. Show what you can do with it. Example before: "Email isn't just for communication—it's where business data already lives..." Example after: "You should be able to forward a vendor email to create a task, or have a customer inquiry automatically update your CRM."

   6. **Make CTAs specific with direct links.** No vague "check it out" or "learn more." Always include the actual link, date, or next step inline so the reader doesn't have to hunt for it.


13. **Populate the README "Key Takeaways" from the finished email**

   The email.md is the source of truth for the takeaways. Once it is fully written and humanized (step 12), back-fill the episode README's `## Key Takeaways` section so the two stay in sync. Do this LAST, after the email is final, not from the raw transcript.

   - Open the target episode's `README.md`. The `## Key Takeaways` section is usually present but empty (header immediately followed by `## Resources`). If the header is missing entirely, create it in the same position sibling episodes use (after `## Whiteboards`, before `## Resources`).
   - Read the finished `email.md`. Its bolded points (and the "if you remember one thing" closer) ARE the takeaways. Distill them into **4-6 bullets**.
   - Match the established house style exactly. Each bullet is a bold lead sentence stating the insight, followed by a concrete supporting explanation drawn from the email, usually with a specific example. Use backticks for code/technical terms. For example:
     ```markdown
     - **Code mode's biggest win is output shaping.** In bash, getting only the PR URL from `gh pr create` means piping through `jq` and hoping the model remembers to do it. In code mode, you write `const prResult = await tools.github.createPR(); console.log(prResult.url)` and only that URL goes into context.
     ```
   - Draw ONLY from the email content. Do not invent facts that aren't in the email.
   - Preserve structure: `## Key Takeaways`, blank line, the bullets, blank line, the next header. Do not modify any other part of the README.
   - Reference a recent filled-in example (e.g. `2026-05-12-code-mode-deep-dive/README.md`) to confirm the style before writing.
   - When completing several episodes at once, this step is independent per folder and can be delegated to one subagent per episode in parallel.


## Email Notes
- Keep the tone conversational but informative
- Focus on actionable takeaways readers can apply immediately
- The "If you remember one thing" should be the most important concept
- Links should use the actual GitHub structure: `https://github.com/hellovai/ai-that-works/tree/main/[EPISODE-DIR]`

## Important Notes
- Use TodoWrite to track progress through these steps
- Think deeply about the structure and format before making changes
- Verify all information is present before proceeding with updates
- Maintain consistency with existing episode documentation format
- The YouTube thumbnail is REQUIRED - reference 2025-07-08-context-engineering/README.md as a working example
