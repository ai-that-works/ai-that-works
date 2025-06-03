import crypto from 'crypto';
import { Thread } from '../src/agent';
import { Response } from 'express';
import fs from 'fs/promises';
import path from 'path';

export interface ThreadStore {
    create(thread: Thread): Promise<string>;
    get(id: string): Promise<Thread | undefined>;
    update(id: string, thread: Thread): Promise<void>;
}

// you can replace this with any simple state management,
// e.g. redis, sqlite, postgres, etc
export class FileSystemThreadStore implements ThreadStore {
    private threadsDir: string;
    
    constructor() {
        this.threadsDir = path.join(process.cwd(), '.threads');
    }
    
    async create(thread: Thread): Promise<string> {
        await fs.mkdir(this.threadsDir, { recursive: true });
        const id = crypto.randomUUID();
        const filePath = path.join(this.threadsDir, `${id}.json`);
        const txtPath = path.join(this.threadsDir, `${id}.txt`);
        await Promise.all([
            fs.writeFile(filePath, JSON.stringify(thread, null, 2)),
            fs.writeFile(txtPath, thread.serializeForLLM())
        ]);
        return id;
    }
    
    async get(id: string): Promise<Thread | undefined> {
        const filePath = path.join(this.threadsDir, `${id}.json`);
        const data = await fs.readFile(filePath, 'utf8').catch(() => null);
        if (!data) return undefined;
        return new Thread(JSON.parse(data).events);
    }

    async update(id: string, thread: Thread): Promise<void> {
        const filePath = path.join(this.threadsDir, `${id}.json`);
        const txtPath = path.join(this.threadsDir, `${id}.txt`);
        await Promise.all([
            fs.writeFile(filePath, JSON.stringify(thread, null, 2)),
            fs.writeFile(txtPath, thread.serializeForLLM())
        ]);
    }
}