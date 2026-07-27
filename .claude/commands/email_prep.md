# Email Generation Command

## Step 1: Determine Target Directory
If this command is invoked with no arguments, ask the user which episode directory to generate an email for.

## Step 2: Get the Required Information
- Get the episode title from the `meta.md` in the directory
- Get the episode description from the `meta.md` in the directory

**STOP make sure you have the above information before continuing. If you are missing any of them, ask the user for them.**

## Step 3:
Make sure there is a `transcript.txt` file in the directory. If there isn't, ask the user for the transcript.

## Step 3: Generate the Email JSON
Use the provided information to run the cli:
```bash
   cd 2026-02-17-automating-aitw
   uv run python -m src.email_generator.generate_email --title <provided episode title> --description <provided description> --transcript <path to transcript> --output <path to episode directory>
```

## Step 4: Convert to a email.md
Convert the outputted json to an `email.md`

## Step 5: Read Context
1. List all email.md files: `*/email.md`
2. Read at least 3 recent email.md files to understand the tone, structure, and style
3. Read the README.md from the target episode directory to understand the content

## Step 6: Analyze Email Structure
Emails typically follow this format:
- **Greeting**: "Hello First Name,"
- **Opening**: Reference to "This week's 🦄 ai that works session" with the topic
- **Links**: GitHub repo link and YouTube video link
- **Key Takeaways**: 3-5 numbered or bulleted actionable insights
- **Memorable Quote**: "If you remember one thing from this session:" or "key takeaway" or something similar as a section
- **Next Session**: Information about tomorrow's session with Luma link (this email gets sent out the day before another session)
- **Call to Action**: Discord link, questions invitation
- **Sign-off**: "Happy coding 🧑‍💻" followed by "Vaibhav & Dex" or similar

## Step 7: Humanize the Email
These emails often come sound like AI slop. Rewrite the email, applying the following rules to make it sound more human-like:
   1. Remove any repetitive "It's not X, it's Y" or an overreliance on em-dashes. Humans don't write like that.
   2. Vary sentence length.
   3. Replace abstract concepts with concrete examples. Push the concepts to include specific "for example" moments that readers can immediately picture. Example before this rule: "Email agents must handle cancellations, corrections, and race conditions." Example after this rule: "when a user sends a follow-up saying 'actually no, I have an onsite' five seconds after their first email, the system needs to handle that gracefully."
   4. Convert descriptions into actionable implications. Don't just explain what something is. Show what you can do with it. Example before this rule: "Email isn't just for communication—it's where business data already lives..." Example after this rule: "You should be able to forward a vendor email to create a task, or have a customer inquiry automatically update your CRM."
   5. Make call to actions specific with direct links. Generated emails frequently have vague CTAs ("check it out", "learn more"). Always add the specific link, date, or next step so the reader doesn't have to hunt for it.


## Notes
- Keep the tone conversational but informative
- Focus on actionable takeaways readers can apply immediately
- The "If you remember one thing" should be the most important concept
- Links should use the actual GitHub structure: `https://github.com/hellovai/ai-that-works/tree/main/[EPISODE-DIR]`