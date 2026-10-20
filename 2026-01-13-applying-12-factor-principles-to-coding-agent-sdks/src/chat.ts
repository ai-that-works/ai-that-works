import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";
import { query, type SDKUserMessage } from "./agent-sdk";
import { BLUE, GREEN, RESET, createInputQueue, log, printEvent } from "./utils";

async function main() {
  const rl = createInterface({ input: stdin, output: stdout });
  const inputQueue = createInputQueue<string>();

  log(`${BLUE}[System]${RESET} Interactive Chat Demo`);
  log(`${BLUE}[System]${RESET} Type EXIT to quit\n`);

  const firstPrompt = await rl.question(`${GREEN}>${RESET} `);
  if (!firstPrompt || firstPrompt === "EXIT") {
    rl.close();
    return;
  }

  inputQueue.push(firstPrompt);
  let sessionId = "";

  const messageGenerator = async function* (): AsyncIterable<SDKUserMessage> {
    while (true) {
      const input = await inputQueue.pull();
      if (input === null) return;
      log(`${GREEN}[User]${RESET} ${input}`);
      yield {
        type: "user",
        session_id: sessionId,
        parent_tool_use_id: null,
        message: { role: "user", content: input },
      };
    }
  };

  const conversation = query({
    prompt: messageGenerator(),
  });

  for await (const msg of conversation) {
    printEvent(msg);

    if (msg.type === "system" && msg.subtype === "init") {
      sessionId = msg.session_id;
    }

    if (msg.type === "result" && msg.subtype === "success") {
      const nextInput = await rl.question(`\n${GREEN}>${RESET} `);
      if (!nextInput || nextInput === "EXIT") {
        inputQueue.close();
      } else {
        inputQueue.push(nextInput);
      }
    }
  }

  rl.close();
}

main();
