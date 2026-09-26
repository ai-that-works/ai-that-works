import { stderr } from "node:process";
import type { SDKMessage } from "./agent-sdk";

// ============================================================================
// Colors
// ============================================================================

export const RESET = "\x1b[0m";
export const YELLOW = "\x1b[33m";
export const BLUE = "\x1b[34m";
export const GREEN = "\x1b[32m";
export const CYAN = "\x1b[36m";
export const PURPLE = "\x1b[35m";
export const LIGHT_PURPLE = "\x1b[95m";

// ============================================================================
// Logging Helpers
// ============================================================================

export const log = (msg: string) => stderr.write(msg + "\n");
export const truncate = (s: string, len = 120) =>
  s.length > len ? `${s.slice(0, len)}...` : s;
export const oneLine = (s: string) => s.replace(/\n/g, "\\n");

// ============================================================================
// Event Printing
// ============================================================================

export function printEvent(msg: SDKMessage) {
  switch (msg.type) {
    case "system":
      log(`${BLUE}[System]${RESET} ${msg.subtype || "init"}`);
      break;
    case "user": {
      const content = msg.message?.content;
      if (typeof content === "string") {
        log(`${GREEN}[User]${RESET} ${truncate(oneLine(content))}`);
      } else if (Array.isArray(content)) {
        for (const block of content) {
          if (block.type === "tool_result") {
            const response =
              typeof block.content === "string"
                ? block.content
                : JSON.stringify(block.content);
            log(`  -> ${LIGHT_PURPLE}[Response]${RESET} ${truncate(oneLine(response))}`);
          } else if (block.type === "text") {
            log(`${GREEN}[User]${RESET} ${truncate(oneLine(block.text || ""))}`);
          }
        }
      }
      break;
    }
    case "assistant": {
      const content = msg.message?.content;
      if (typeof content === "string") {
        log(`${YELLOW}[Assistant]${RESET} ${truncate(oneLine(content))}`);
      } else if (Array.isArray(content)) {
        for (const block of content) {
          if (block.type === "text") {
            log(`${YELLOW}[Assistant]${RESET} ${truncate(oneLine(block.text || ""))}`);
          } else if (block.type === "tool_use") {
            log(`${PURPLE}[Tool]${RESET} ${block.name}(${truncate(JSON.stringify(block.input))})`);
          }
        }
      }
      break;
    }
    case "result": {
      log(`${YELLOW}[Result]${RESET} ${msg.subtype || "done"}`);
      const structured = (msg as any).structured_output;
      if (structured) {
        log(`${CYAN}[Output]${RESET} ${JSON.stringify(structured, null, 2)}`);
      }
      break;
    }
  }
}

// ============================================================================
// Input Queue - enables multi-turn conversations
// ============================================================================

export function createInputQueue<T>() {
  const pending: T[] = [];
  const waiters: Array<(value: T | null) => void> = [];
  let closed = false;

  return {
    push(value: T) {
      if (closed) return;
      const waiter = waiters.shift();
      if (waiter) waiter(value);
      else pending.push(value);
    },
    async pull(): Promise<T | null> {
      if (closed) return null;
      const value = pending.shift();
      if (value !== undefined) return value;
      return new Promise((resolve) => waiters.push(resolve));
    },
    close() {
      closed = true;
      for (const waiter of waiters) waiter(null);
    },
  };
}
