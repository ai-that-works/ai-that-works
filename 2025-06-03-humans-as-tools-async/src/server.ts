import express, { Request, Response } from 'express';
import { Thread, agentLoop as innerLoop, handleNextStep } from '../src/agent';
import { FileSystemThreadStore, ThreadStore } from '../src/state';
import { ContactChannel, FunctionCall, HumanContact, humanlayer, V1Beta2EmailEventReceived, V1Beta2HumanContactCompleted, V1Beta2SlackEventReceived } from '@humanlayer/sdk';

const app = express();
app.use(express.json());
app.set('json spaces', 2);

const store = new FileSystemThreadStore();

type V1Beta3ConversationCreated = {
    is_test: boolean;
    type: "conversation.created";
    event: {
        user_message: string;
        contact_channel_id: number;
        agent_name: string;
    }
}

type CompletedHumanContact = HumanContact & {
    status: {
        response: string;
    }
}

type V1Veta3HumanContactCompleted = {
    is_test: boolean;
    type: "human_contact.completed";
    event: {
        contact_channel_id: number;
    } & CompletedHumanContact
}

type Approved = {status: {approved: true}}
type Rejected = {status: {approved: false; comment: string}}

type CompletedFunctionCall = FunctionCall & (Approved | Rejected)

type V1Beta3FunctionCallCompleted = {
    is_test: boolean;
    type: "function_call.completed";
    event: {
        contact_channel_id: number;
    } & CompletedFunctionCall
}

type V1Beta3Event = V1Beta3ConversationCreated | V1Veta3HumanContactCompleted | V1Beta3FunctionCallCompleted;

const notFound = (res: Response) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Thread not found`,
        status: 404
    });
}

const outerLoop = async (req: Request, res: Response) => {
    console.log("outerLoop", req.body);
    const body = req.body as V1Beta3Event;
    const hl = humanlayer({
        runId: process.env.HUMANLAYER_RUN_ID || `12fa-agent`,
        contactChannel: {
            channel_id: body.event.contact_channel_id,
        } as ContactChannel // todo export this type flavor
    });

    /* get the thread or make a new one*/
    let thread: Thread | undefined;
    let threadId: string | undefined;
    switch (body.type) {
        case "conversation.created":
            thread = new Thread([{type: "conversation.created", data: body.event.user_message}]);
            break;
        case "human_contact.completed":
        case "function_call.completed":
            threadId = body.event.spec.state?.thread_id;
            if (!threadId) {
                notFound(res);
                return;
            }
            thread = store.get(threadId);
            if (!thread) {
                notFound(res);
                return;
            }
            break;
    }


    /* handle the response event */
    if (body.type === "function_call.completed" && body.event.status?.approved) {
        // run the function call and add the result to the thread
        thread = await handleNextStep(thread.lastEvent().data, thread);
    } else if (body.type === "function_call.completed" && !body.event.status?.approved) {
        // add the denial to the thread
        thread.events.push({
            type: "human_response", 
            data: `user denied operation ${thread.lastEvent().data.intent} with feedback: ${body.event.status?.comment}`
        });
    } else if (body.type === "human_contact.completed") {
        // add the human response to the thread
        thread.events.push({
            type: "human_response",
            data: {
                msg: body.event.status.response,
            }
        });
    }

    /* run the inner loop */
    await Promise.resolve().then(async() => {
        const newThread = await innerLoop(thread);
        if (threadId) {
            store.update(threadId, newThread);
        } else {
            threadId = store.create(newThread);
        }
        // we exited the inner loop, send to human
        const lastEvent = newThread.lastEvent();
        switch (lastEvent.data.intent) {
            case "request_more_information":
            case "done_for_now":
                hl.createHumanContact({
                    spec: {
                        msg: lastEvent.data.message,
                        state: {
                            thread_id: threadId
                        }
                    }
                });
                console.log(`created human contact "${lastEvent.data.message}"`);
                break;
            case "other_scary_tools":  // example, add more tools here
            case "divide":
                const intent = lastEvent.data.intent;
                // remove intent from kwargs payload
                const { intent: _, ...kwargs } = lastEvent.data;
                hl.createFunctionCall({
                    spec: {
                        fn: intent,
                        kwargs: kwargs,
                        state: {
                            thread_id: threadId
                        }
                    }
                });
                console.log("created function call", {intent, kwargs});
                break;
        }
    });
    res.json({ status: "ok" });
}

export const startServer = () => {
    app.post('/api/v1/conversations', outerLoop)
    
    // Handle 404 - Not Found
    app.use((req: Request, res: Response) => {
        res.status(404).json({
            error: 'Not Found',
            message: `Route ${req.originalUrl} not found`,
            status: 404
        });
    });
    
    const port = process.env.PORT || 8000;
    const server = app.listen(port, () => {
        console.log(`Server is running on port ${port}`);
    });

    server.on('error', (error: Error) => {
        console.error('Server error:', error);
    });

    return server;
}

// Only start the server if this file is being run directly
if (require.main === module) {
    startServer();
}