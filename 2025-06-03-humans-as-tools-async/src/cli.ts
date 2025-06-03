// cli.ts lets you invoke the agent loop from the command line

import { humanlayer } from "humanlayer";
import { agentLoop, Thread, Event, handleNextStep } from "../src/agent";
import { FileSystemThreadStore } from "./state";
import chalk from "chalk";

const threadStore = new FileSystemThreadStore();

export async function cliOuterLoop(message: string) {
    // Create a new thread with the user's message as the initial event
    const thread = new Thread([{ type: "user_input", data: message }]);
    const threadId = await threadStore.create(thread);

    // Run the agent loop with the thread

    // loop until ctrl+c
    // optional, you could exit on done_for_now and print the final result
    // while (lastEvent.data.intent !== "done_for_now") {
    while (true) {
        let newThread = await agentLoop(thread);
        await threadStore.update(threadId, newThread);
        let lastEvent = newThread.lastEvent();

        // everything on CLI
        const responseEvent = await askHumanCLI(lastEvent);
        newThread.events.push(responseEvent);
        // if (lastEvent.data.intent === "request_approval_from_manager") {
        //     const responseEvent = await askManager(lastEvent);
        //     thread.events.push(responseEvent);
        // } else {
        //     const responseEvent = await askHumanCLI(lastEvent);
        //     thread.events.push(responseEvent);
        // }
        await threadStore.update(threadId, newThread);
    }
}

export async function cli() {
    // Get command line arguments, skipping the first two (node and script name)
    const args = process.argv.slice(2);

    const message = args.length === 0 ? "hello!" : args.join(" ");

    await cliOuterLoop(message);
}

// async function askManager(lastEvent: Event): Promise<Event> {
//     const hl = humanlayer({
//         contactChannel: {
//              email: {
//                 address: process.env.HUMANLAYER_EMAIL_ADDRESS || "manager@example.com"
//             }
//         }
//     })
//     const resp = await hl.fetchHumanResponse({
//         spec: {
//             msg: lastEvent.data.message
//         }
//      })
//      return {
//         type: "manager_response",
//         data: resp
//      }
// }

async function askHumanCLI(lastEvent: Event): Promise<Event> {

    switch (lastEvent.data.intent) {
        case "divide":
            const response = await approveCLI(`agent wants to run ${chalk.green(JSON.stringify(lastEvent.data))}\nPress Enter to approve, or type feedback to cancel:`);
            if (response.approved) {
                const thread = new Thread([lastEvent]);
                const result = await handleNextStep(lastEvent.data, thread);
                return result.events[result.events.length - 1];
            } else {
                return {
                    type: "tool_response",
                    data: `user denied operation ${lastEvent.data.intent} with feedback: ${response.comment}`
                };
            }
        case "request_more_information":
        case "request_approval_from_manager":
        case "done_for_now":
            const message = await messageCLI(lastEvent.data.message);
            return {
                type: "tool_response",
                data: message
            };
        default:
            throw new Error(`unknown tool in outer loop: ${lastEvent.data.intent}`)
    }
}

type Approval = {
    approved: true;
} | {
    approved: false;
    comment: string;
}
async function messageCLI(message: string): Promise<string> {
    const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        readline.question(`${message}\n> `, (answer: string) => {
            readline.close();
            resolve(answer);
        });
    });
}

async function approveCLI(message: string): Promise<Approval> {
    const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
    });

    return new Promise((resolve) => {
        readline.question(`${message}\n> `, (answer: string) => {
            readline.close();
            // If the answer is empty (just pressed enter), treat it as approval
            if (answer.trim() === '') {
                resolve({ approved: true });
            } else {
                // Any non-empty response is treated as rejection with feedback
                resolve({ approved: false, comment: answer });
            }
        });
    });
}


if (require.main === module) {
    cli()
}