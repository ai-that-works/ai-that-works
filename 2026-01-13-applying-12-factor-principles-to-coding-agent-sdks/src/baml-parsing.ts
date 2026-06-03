/**
 * BAML Parsing Example
 *
 * Get natural language from Claude Agent SDK, parse with BAML.
 * Alternative to SDK's built-in structured output.
 */

import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";
import { query } from "./agent-sdk";
import { b } from "./baml_client";
import { BLUE, CYAN, GREEN, RESET, YELLOW, log, printEvent } from "./utils";

async function main() {
  const rl = createInterface({ input: stdin, output: stdout });

  log(`${BLUE}[System]${RESET} BAML Parsing Demo\n`);

  const task = process.argv[2] || (await rl.question(`${GREEN}Task>${RESET} `));
  if (!task) {
    rl.close();
    return;
  }

  rl.close();

  // Step 1: Get natural language from agent (no structured output)
  log(`${CYAN}=== Step 1: Get Design Discussion ===${RESET}\n`);
  log(`${GREEN}[User]${RESET} ${task}`);

  const conversation = query({
    prompt: `You are helping design a feature: ${task}

Think through the design and list any open questions you'd need answered.
Write naturally - summarize your understanding then list questions.`,
  });

  let response = "";
  for await (const msg of conversation) {
    printEvent(msg);
    if (msg.type === "assistant") {
      const content = msg.message?.content;
      if (typeof content === "string") response += content;
      else if (Array.isArray(content)) {
        for (const block of content) {
          if (block.type === "text") response += block.text || "";
        }
      }
    }
  }

  log(`\n${YELLOW}[Raw Response]${RESET}\n${response}\n`);

  // Step 2: Parse with BAML
  log(`${CYAN}=== Step 2: Parse with BAML ===${RESET}\n`);

  const parsed = await b.ParseDesignDiscussion(response);

  log(`${CYAN}[Parsed Output]${RESET}`);
  log(JSON.stringify(parsed, null, 2));
}

main();
