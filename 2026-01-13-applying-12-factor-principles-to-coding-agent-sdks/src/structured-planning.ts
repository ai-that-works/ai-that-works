import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";
import { query, type SDKUserMessage } from "./agent-sdk";
import { z } from "zod";
import {
  BLUE,
  CYAN,
  GREEN,
  RESET,
  createInputQueue,
  log,
  printEvent,
} from "./utils";

// ============================================================================
// Step 1: Design Discussion
// ============================================================================

const Step1OutputSchema = z.object({
  summary: z.string().describe("Summary of design decisions so far"),
  openDesignQuestions: z
    .array(z.string())
    .describe("Questions that still need answers - empty when design is complete"),
});

type Step1Output = z.infer<typeof Step1OutputSchema>;

async function step1DesignDiscussion(
  task: string,
  rl: ReturnType<typeof createInterface>,
): Promise<Step1Output> {
  log(`\n${CYAN}=== Step 1: Design Discussion ===${RESET}\n`);

  const inputQueue = createInputQueue<string>();
  const { $schema: _, ...schema } = z.toJSONSchema(Step1OutputSchema);

  let sessionId = "";
  let output: Step1Output | undefined;

  const initialPrompt = `You are helping design a feature. Explore the codebase and ask clarifying questions.

Task: ${task}

Research the codebase, then ask questions about how the user wants to implement this.
When all design questions are answered, set openDesignQuestions to an empty array.`;

  inputQueue.push(initialPrompt);
  log(`${GREEN}[User]${RESET} ${task}`);

  const messageGenerator = async function* (): AsyncIterable<SDKUserMessage> {
    while (true) {
      const input = await inputQueue.pull();
      if (input === null) return;
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
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  for await (const msg of conversation) {
    printEvent(msg);

    if (msg.type === "system" && msg.subtype === "init") {
      sessionId = msg.session_id;
    }

    if (msg.type === "result" && msg.subtype === "success") {
      output = (msg as any).structured_output;

      if (output && output.openDesignQuestions.length === 0) {
        log(`${CYAN}[Phase Complete]${RESET} No open design questions`);
        inputQueue.close();
      } else if (output) {
        log(`\n${CYAN}Open Questions:${RESET}`);
        output.openDesignQuestions.forEach((q) => log(`  - ${q}`));
        log("");

        const answer = await rl.question(`${GREEN}>${RESET} `);
        if (!answer || answer === "EXIT") {
          inputQueue.close();
        } else {
          log(`${GREEN}[User]${RESET} ${answer}`);
          inputQueue.push(answer);
        }
      }
    }
  }

  if (!output) throw new Error("Step 1 failed");
  return output;
}

// ============================================================================
// Step 2: Structure Outline
// ============================================================================

const Step2OutputSchema = z.object({
  title: z.string(),
  phases: z.array(
    z.object({
      name: z.string(),
      description: z.string(),
    }),
  ),
  userApprovedOutline: z
    .boolean()
    .describe("True when user has approved the outline"),
});

type Step2Output = z.infer<typeof Step2OutputSchema>;

async function step2StructureOutline(
  task: string,
  designSummary: string,
  rl: ReturnType<typeof createInterface>,
): Promise<Step2Output> {
  log(`\n${CYAN}=== Step 2: Structure Outline ===${RESET}\n`);

  const inputQueue = createInputQueue<string>();
  const { $schema: _, ...schema } = z.toJSONSchema(Step2OutputSchema);

  let sessionId = "";
  let output: Step2Output | undefined;

  const initialPrompt = `Create a phased implementation outline based on this design:

Task: ${task}
Design Summary: ${designSummary}

Propose phases and iterate with the user. Set userApprovedOutline to true when they approve.`;

  inputQueue.push(initialPrompt);

  const messageGenerator = async function* (): AsyncIterable<SDKUserMessage> {
    while (true) {
      const input = await inputQueue.pull();
      if (input === null) return;
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
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  for await (const msg of conversation) {
    printEvent(msg);

    if (msg.type === "system" && msg.subtype === "init") {
      sessionId = msg.session_id;
    }

    if (msg.type === "result" && msg.subtype === "success") {
      output = (msg as any).structured_output;

      if (output?.userApprovedOutline) {
        log(`${CYAN}[Phase Complete]${RESET} Outline approved`);
        inputQueue.close();
      } else if (output) {
        log(`\n${CYAN}Proposed Outline:${RESET} ${output.title}`);
        output.phases.forEach((p, i) => log(`  ${i + 1}. ${p.name}: ${p.description}`));
        log(`\nType APPROVE to accept, or provide feedback:`);

        const answer = await rl.question(`${GREEN}>${RESET} `);
        if (!answer || answer === "EXIT") {
          inputQueue.close();
        } else if (answer === "APPROVE") {
          log(`${GREEN}[User]${RESET} Approved`);
          inputQueue.push("The user approves this outline. Set userApprovedOutline to true.");
        } else {
          log(`${GREEN}[User]${RESET} ${answer}`);
          inputQueue.push(answer);
        }
      }
    }
  }

  if (!output) throw new Error("Step 2 failed");
  return output;
}

// ============================================================================
// Step 3: Write Plan File
// ============================================================================

const Step3OutputSchema = z.object({
  title: z.string(),
  overview: z.string(),
  phases: z.array(
    z.object({
      name: z.string(),
      tasks: z.array(z.string()),
      successCriteria: z.array(z.string()),
    }),
  ),
});

type Step3Output = z.infer<typeof Step3OutputSchema>;

async function step3WritePlan(
  task: string,
  outline: Step2Output,
): Promise<Step3Output> {
  log(`\n${CYAN}=== Step 3: Write Plan File ===${RESET}\n`);

  const { $schema: _, ...schema } = z.toJSONSchema(Step3OutputSchema);

  const prompt = `Write a detailed implementation plan:

Title: ${outline.title}
Phases:
${outline.phases.map((p) => `- ${p.name}: ${p.description}`).join("\n")}

Original task: ${task}`;

  const conversation = query({
    prompt,
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  let output: Step3Output | undefined;

  for await (const msg of conversation) {
    printEvent(msg);
    if (msg.type === "result" && msg.subtype === "success") {
      output = (msg as any).structured_output;
    }
  }

  if (!output) throw new Error("Step 3 failed");
  return output;
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  const rl = createInterface({ input: stdin, output: stdout });

  log(`${BLUE}[System]${RESET} Structured Planning Demo`);
  log(`${BLUE}[System]${RESET} Flow: Design Discussion -> Structure Outline -> Write Plan\n`);

  const task = process.argv[2] || (await rl.question(`${GREEN}Task>${RESET} `));
  if (!task) {
    rl.close();
    return;
  }

  const step1 = await step1DesignDiscussion(task, rl);
  const step2 = await step2StructureOutline(task, step1.summary, rl);
  const step3 = await step3WritePlan(task, step2);

  log(`\n${CYAN}=== Final Plan ===${RESET}`);
  log(JSON.stringify(step3, null, 2));

  rl.close();
}

main();
