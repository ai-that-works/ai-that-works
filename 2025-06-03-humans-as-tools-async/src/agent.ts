import { AddTool, SubtractTool, DivideTool, MultiplyTool, b, ProcessRefund } from "../baml_client";

export interface Event {
    type: string
    data: any;
}

export class Thread {
    
    events: Event[] = [];

    strictPrompt: boolean = false;

    workingAgent: string = "success-agent";

    constructor(events: Event[]) {
        this.events = events;
    }

    serializeForLLM() {
        return this.events.map(e => this.serializeOneEvent(e)).join("\n");
    }

    trimLeadingWhitespace(s: string) {
        return s.replace(/^[ \t]+/gm, '');
    }

    serializeOneEvent(e: Event) {
        return this.trimLeadingWhitespace(`
            <${e.data?.intent || e.type}>
            ${
            typeof e.data !== 'object' ? e.data :
            Object.keys(e.data).filter(k => k !== 'intent').map(k => `${k}: ${e.data[k]}`).join("\n")}
            </${e.data?.intent || e.type}>
        `)
    }

    awaitingHumanResponse(): boolean {
        const lastEvent = this.events[this.events.length - 1];
        return ['request_more_information', 'done_for_now'].includes(lastEvent.data.intent);
    }

    awaitingHumanApproval(): boolean {
        const lastEvent = this.events[this.events.length - 1];
        return lastEvent.data.intent === 'divide';
    }

    lastEvent(): Event {
        return this.events[this.events.length - 1];
    }
}

export type CalculatorTool = AddTool | SubtractTool | MultiplyTool | DivideTool;

export async function handleNextStep(nextStep: CalculatorTool | ProcessRefund, thread: Thread): Promise<Thread> {
    let result: number;
    switch (nextStep.intent) {
        case "add":
            result = nextStep.a + nextStep.b;
            console.log("tool_response", result);
            thread.events.push({
                "type": "tool_response",
                "data": result
            });
            return thread;
        case "subtract":
            result = nextStep.a - nextStep.b;
            console.log("tool_response", result);
            thread.events.push({
                "type": "tool_response",
                "data": result
            });
            return thread;
        case "multiply":
            result = nextStep.a * nextStep.b;
            console.log("tool_response", result);
            thread.events.push({
                "type": "tool_response",
                "data": result
            });
            return thread;
        case "divide":
            result = nextStep.a / nextStep.b;
            console.log("tool_response", result);
            thread.events.push({
                "type": "tool_response",
                "data": result
            });
            return thread;
        case "process_refund":
            thread.events.push({
                "type": "tool_response",
                "data": "refund processed successfully"
            });
            return thread;
    }
}

export async function agentLoop(thread: Thread): Promise<Thread> {
    while (true) {
        const nextStep = await b.DetermineNextStep(thread.serializeForLLM());

        console.log("nextStep", nextStep);

        thread.events.push({
            "type": "tool_call",
            "data": nextStep
        });

        switch (nextStep.intent) {
            case "done_for_now":
            case "request_more_information":
            // case "request_approval_from_manager":
                // response to human, return the thread
                return thread;
            case "divide":
            case "process_refund":
                // divide and process_refund is scary, return it for human approval
                return thread;
            case "add":
            case "subtract":
            case "multiply":
                thread = await handleNextStep(nextStep, thread);
        }
    }
}


