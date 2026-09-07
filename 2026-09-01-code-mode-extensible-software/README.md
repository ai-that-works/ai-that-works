# 🦄 ai that works: Code Mode for Extensible Software

> Making software extensible has always meant designing good, flexible interfaces, think VS Code extensions or iPhone apps. Vaibhav argues the most flexible interface of all is code itself, and walks through what the next generation of customizable tools looks like when agents write code instead of calling tools.

[Video](https://www.youtube.com/watch?v=IXe48aIw_X4)

[![Code Mode for Extensible Software](https://img.youtube.com/vi/IXe48aIw_X4/0.jpg)](https://www.youtube.com/watch?v=IXe48aIw_X4)

Links:

- [Session Code](https://github.com/ai-that-works/ai-that-works/tree/main/2026-09-01-code-mode-extensible-software)

## Episode Highlights

> "You're inventing a shitty DSL on top of something that's well described." (on JSON tool schemas with dozens of properties)

> "There's no frickin' way you can execute tools at the speed of code if you're using an LLM to decide what tools to call."

> "Letting untrusted code touch an object prototype is incredibly evil. You have to sandbox it."

## Key Takeaways

- **The bash tool is already code mode, you've just been using it this whole time.** Instead of the agent calling `read`, then `grep`, then `glob` as three separate round trips to the model, you hand it a shell and let it write `cat file | grep pattern`. Harnesses are quietly collapsing separate list-files/grep-files/glob-files tools into "just give it bash" because the agent already knows how to compose Unix tools.
- **A JSON tool with forty properties is a shitty DSL you invented on top of something the model already understands.** HumanLayer needed an agent to edit a YJS CRDT (a rich text document synced live across a network). Instead of a bloated tool interface for traversing the tree node by node, they let the agent write JavaScript directly against a YJS-shaped API, since YJS is already deep in the training data.
- **Round-tripping the model to edit a live document means the document changes out from under you mid-edit.** Ten tool calls to traverse and update a CRDT means ten full inference round trips, and other users could be editing that same document the whole time. Code mode collapses that into one generated string that executes as a single atomic operation, running at code speed instead of ~300ms per hop, ten times over.
- **If you're running untrusted agent code in a multi-tenant backend, you can't just eval it, you have to build bindings.** HumanLayer runs generated JavaScript inside `QuickJS` instead of Node, exposing only specific functions hardcoded to the current user's ID. Reflection, the filesystem, and shell are denied by default, since letting untrusted code touch a real object prototype is how you get prototype-pollution RCEs.
- **BAML's take pushes further: type-check the generated code before you ever run it.** Passing a chunk of generated code as a string and running a compile-time check (catching something like calling `.split()` on a value that has to stay a plain string) before execution means a broken contract gets caught before a side-effectful operation, like a partially applied CRDT edit, leaves things in an unknown state.

## Resources

- [Session Recording](https://www.youtube.com/watch?v=IXe48aIw_X4)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

## Whiteboards
