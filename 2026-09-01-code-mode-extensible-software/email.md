Hello {firstName},

This week's 🦄 ai that works session was Vaibhav and Kyle Mistele (HumanLayer co-founder) digging into code mode: what it actually is, why it's suddenly everywhere, and two very different real implementations of it.

The full recording is on [YouTube](https://www.youtube.com/watch?v=IXe48aIw_X4), and the code is on [GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-01-code-mode-extensible-software).

**The bash tool is already code mode, you've just been using it this whole time.** Kyle's framing: instead of the agent calling read, then grep, then glob as three separate round trips to the model, you hand it a shell and let it write `cat file | grep pattern`. Claude Code used to have separate list-files, grep-files, and glob-files tools. A lot of harnesses are quietly collapsing those into "just give it bash" because the agent already knows how to compose Unix tools, so why teach it a worse version of the same thing.

**A JSON tool with forty properties is a shitty DSL you invented on top of something the model already understands.** HumanLayer needed an agent to edit a YJS CRDT (think a Google Docs style rich text document being synced live across a network). The naive approach is a tool interface for traversing the tree, like "get node ID, then edit node," which turns into exactly the kind of bloated JSON schema models are bad at. Instead they let the agent write JavaScript directly against a YJS-shaped API, because YJS is one of the most common CRDT libraries out there and the model already knows it cold.

**Round-tripping the model to edit a live document means the document changes out from under you mid-edit.** If an agent needs ten tool calls to traverse and update a CRDT, each one is a full inference round trip, and other users could be editing that same document the whole time. By the time the tenth call finishes, the edit might not even make sense anymore. Code mode collapses that into one generated string that executes as a single atomic operation, so the agent decides once and the whole thing runs at code speed instead of "wait 300ms per hop, ten times."

**If you're running untrusted agent code in a multi-tenant backend, you can't just eval it, you have to build bindings.** HumanLayer runs the generated JavaScript inside QuickJS (a small C-based JS runtime that compiles to WASM) instead of Node, and it only exposes specific functions they've explicitly injected, hardcoded to the current user's ID so a session can never touch another tenant's data. Letting untrusted code touch a real object prototype is how you get prototype-pollution RCEs, so reflection, the filesystem, and shell all get denied by default and only turned on deliberately.

**BAML's take pushes further: type-check the generated code before you ever run it.** Vaibhav showed passing a chunk of generated code as a string, having it fail a compile-time check when the types don't line up (like calling `.split()` on something that has to stay a plain string), and only executing once it type-checks clean. For something with side effects, like partially applying a CRDT edit, catching a broken contract before execution beats discovering halfway through that you can't finish the operation and don't know what state you're in.

**If you remember one thing from this session:**

Code mode isn't really about saving tokens, it's about not designing a worse interface than the one that already exists. Every time you're tempted to build a custom tool schema for something a model already knows well, like SQL, YJS, or a shell, ask whether you're really protecting anything or just making the agent relearn something it already speaks fluently.

**Next session: Software Factories, Hands-On With Real Builders, September 8th**

We had some genuinely great unconference talks from people actually building software factories week over week with background agents that keep getting smarter. This week we're bringing those builders onto the show to talk about how they run it in practice. Sign up here: https://luma.com/hands-on-software-factories

If you have questions, reply to this email or hop into [Discord](https://boundaryml.com/discord). We read everything.

Happy coding 🧑‍💻

Vaibhav & Dex
