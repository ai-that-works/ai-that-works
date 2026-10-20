import { query } from "./agent-sdk";
import { BLUE, GREEN, RESET, log, printEvent } from "./utils";

async function main() {
  log(`${BLUE}[System]${RESET} Starting hello world demo...`);

  const prompt = "Say hello world and nothing else";
  log(`${GREEN}[User]${RESET} ${prompt}`);

  const conversation = query({
    prompt,
  });

  for await (const message of conversation) {
    printEvent(message);
  }
}

main();
