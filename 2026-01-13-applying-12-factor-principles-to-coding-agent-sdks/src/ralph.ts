/**
 * Ralph Wiggum Loop Pattern
 *
 * Based on the "Ralph Wiggum" coding agent power tools episode.
 * Key idea: One loop, one step. Exit. Rerun. Don't convince the model
 * to work longer; bound the work instead.
 *
 * This translates the bash loop:
 *   while true; do
 *     cat PROMPT.md | claude -p --dangerously-skip-permissions --output-format=stream-json
 *     sleep 10
 *   done
 */

import { readFileSync, existsSync } from "node:fs";
import { stdin } from "node:process";
import { query } from "./agent-sdk";
import { BLUE, CYAN, RESET, YELLOW, log, printEvent } from "./utils";

const LOOP_DELAY_MS = 10000;
const SINGLE_RUN = process.argv.includes("--once");

async function readStdin(): Promise<string | null> {
  if (stdin.isTTY) return null;
  const chunks: Buffer[] = [];
  for await (const chunk of stdin) {
    chunks.push(chunk);
  }
  const content = Buffer.concat(chunks).toString("utf-8").trim();
  return content || null;
}

async function getPrompt(): Promise<string> {
  // 1. CLI arg (skip flags)
  const args = process.argv.slice(2).filter((a) => !a.startsWith("--"));
  if (args[0] && !existsSync(args[0])) {
    // It's a prompt string, not a file
    return args[0];
  }

  // 2. stdin
  const stdinContent = await readStdin();
  if (stdinContent) {
    return stdinContent;
  }

  // 3. File (from arg or default)
  const file = args[0] || "PROMPT.md";
  if (existsSync(file)) {
    return readFileSync(file, "utf-8");
  }

  log(`${YELLOW}[Error]${RESET} No prompt provided`);
  log(`\nUsage:`);
  log(`  bun run ralph "your prompt here"       # CLI arg`);
  log(`  echo "prompt" | bun run ralph          # stdin`);
  log(`  bun run ralph PROMPT.md                # file`);
  log(`  bun run ralph --once                   # single iteration`);
  process.exit(1);
}

async function runOnce(prompt: string, iteration: number) {
  log(
    `\n${CYAN}==================== LOOP ${iteration} ====================${RESET}\n`,
  );

  const conversation = query({
    prompt,
    options: {
      permissionMode: "bypassPermissions",
    },
  });

  for await (const msg of conversation) {
    printEvent(msg);
  }
}

async function main() {
  const prompt = await getPrompt();

  log(`${BLUE}[System]${RESET} Ralph Wiggum Loop`);
  log(
    `${BLUE}[System]${RESET} Mode: ${SINGLE_RUN ? "single run" : "infinite loop"}`,
  );
  log(`${BLUE}[System]${RESET} Prompt: ${prompt.slice(0, 100)}...`);

  let iteration = 1;

  if (SINGLE_RUN) {
    await runOnce(prompt, iteration);
    return;
  }

  while (true) {
    await runOnce(prompt, iteration);
    log(`\n${BLUE}[System]${RESET} Sleeping ${LOOP_DELAY_MS}ms...`);
    await new Promise((r) => setTimeout(r, LOOP_DELAY_MS));
    iteration++;
  }
}

main();
