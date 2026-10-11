# 🦄 ai that works: Agentic RAG + Context Engineering

> Exploring the intricacies of building an Agentic Retrieval-Augmented Generation (RAG) system, emphasizing the flexibility and decision-making capabilities that distinguish it from traditional RAG approaches.

[Video](https://www.youtube.com/watch?v=grGSFfyejA0) (1h18m)

[![Agentic RAG + Context Engineering](https://img.youtube.com/vi/grGSFfyejA0/0.jpg)](https://www.youtube.com/watch?v=grGSFfyejA0)

## Episode Summary

Vaibhav Gupta demonstrates building a complete Agentic RAG system from scratch in just 3 hours, showing the crucial difference between deterministic RAG pipelines and agent-driven context assembly. The live coding session reveals that while the agent loop itself is straightforward, the real complexity lies in tool implementation details - from handling relative paths in grep results to managing working directories and truncation notices.

## Key Insights

### Agentic RAG vs Traditional RAG

> "RAG is a system that takes in a user query and looks into some database... Traditional RAG uses vector search 100% of the time. Agentic RAG lets the model decide if it needs to RAG anything at all."

- **Traditional RAG**: Deterministic code fetches context based on vector similarity every time
- **Agentic RAG**: Model decides which tools to use and what context to retrieve
- Trade-off: Flexibility and capability vs speed and predictability

### The 3-Hour Build Breakdown

- **Hour 1**: Basic agent loop and tool definitions (30% hand-written, 70% AI-generated)
- **Hour 2**: Building UI/TUI for effective iteration and debugging
- **Hour 3**: Refining tool implementations based on testing

> "Most of the time actually came from UI time, not from anything else."

### Critical Tool Implementation Details

**What Actually Mattered:**
- Using relative paths instead of absolute paths in grep results
- Tracking and injecting current working directory into prompts
- Adding clear truncation notices with line numbers
- Implementing proper timeouts for all subprocess calls
- Using ripgrep (rg) instead of standard grep

**What Didn't Matter:**
- Tool definition prompts (never changed after initial write)
- Complex retry logic
- Structured tool response formats

### The Architecture Pattern

```
User Query → [Agent Loop with Tools] → Response
           ↓
    Iterations (tool calls)
           ↓
    Tool Results → Back to Agent
```

Each iteration can call tools or respond to user. Sub-agents spawn fresh contexts but can't spawn more sub-agents (preventing infinite recursion).

### Context Engineering Lessons

> "That's context engineering. How do you make it more context efficient? Every single token counts. When you save 20 tokens per call and you're gonna grep 30 times, that makes a huge difference."

**Key Optimizations:**
- Render tools in simplified format, not full JSON
- Use `[Dir]` and `[File]` prefixes in ls output
- Truncate file reads at 20K chars or 5K lines with clear instructions
- Strip HTML to text in web fetch, save full content to file if needed

### Error Handling Philosophy

Instead of forcing models to retry on parse errors, detect intent:
- If response starts with backticks but not JSON → probably meant for user
- Keep error corrections temporary, don't pollute context history
- Add "invalid response" feedback but remove after correction

### When to Use Agentic RAG

**Use Agentic RAG When:**
- Problem scope is unbounded
- User queries vary widely
- You need web search + code search + docs
- Flexibility matters more than speed

**Avoid Agentic RAG When:**
- Problem scope is well-defined
- Speed is critical
- Most queries follow similar patterns
- You can predict needed context

> "Most people should not build agentic RAG systems for their workflows. If you're building a software stack, most problems are not so wide that you need an agentic rag system."

### Model Considerations

- GPT-4o works well out of the box
- Smaller models (GPT-4o-mini) struggle with complex tool orchestration
- Line numbers in file reads work without special training
- RL/fine-tuning helps but isn't required for basic functionality

### The Build Philosophy

> "Writing the code helps me understand how it works. If I use a Claude Agent SDK, I don't actually understand what a system is doing."

Build from first principles to understand:
- System design trade-offs
- Where complexity actually lives
- What optimizations matter
- How to debug when things fail

## Practical Implementation Tips

1. **Start with a baseline**: Build deterministic RAG first, then add agent capabilities
2. **Invest in UI early**: Good debugging UI is crucial for iteration
3. **Test with consistent queries**: Use the same 10 queries repeatedly during development
4. **Track tool sequences**: Focus on which tools are called in what order, not just final output
5. **Handle state carefully**: Preserve working directory, track file modifications
6. **Optimize for context**: Every token saved in tool responses compounds across iterations

## The Bottom Line

Agentic RAG isn't technically complex - you can build one in 3 hours. The challenge is making tools context-efficient and deciding if you actually need the flexibility versus a faster, deterministic pipeline. As Dex summarizes: "The answer is what solves your user's problem."

## Running the Code

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ai-that-works/ai-that-works.git
cd ai-that-works/2025-10-21-agentic-rag-context-engineering

# Install dependencies
uv sync

# Generate BAML client
uv run baml-cli generate

# Set your API keys
export OPENAI_API_KEY="your-key-here"
export EXA_API_KEY="your-exa-key-here"  # Optional, for WebSearch tool

# Run the agent (CLI mode)
uv run python main.py "What files are in this directory?"

# Run in beautiful TUI mode (recommended)
uv run python main.py "Start" --tui

# Interactive mode
uv run python main.py "Start" --interactive
```

### Optional Parallel web tools

Set `WEB_SEARCH_PROVIDER=parallel` to use [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)
for the existing `WebSearch` and `WebFetch` tools in both CLI and TUI mode:

```bash
uv sync
uv run baml-cli generate
export OPENAI_API_KEY="your-key-here"
export WEB_SEARCH_PROVIDER=parallel
uv run python main.py "Search the web for BAML documentation, then fetch the getting started page"
```

This connects over Streamable HTTP to `https://search.parallel.ai/mcp`. No Parallel
account, API key or saved credentials are used. Anonymous search uses Fast mode;
the free service has lower rate limits and is intended for light use. The agent
still needs its model API key. Fetch returns excerpts focused on the first 200
characters of the tool's prompt. Anonymous MCP does not support `allowed_domains`
or `blocked_domains`; requests with these filters return an explicit error.

Unset `WEB_SEARCH_PROVIDER` to keep the existing Exa search and HTML fetching
handlers. Parallel calls have a 60-second overall timeout, propagate task
cancellation and return MCP errors as tool results.

Run the provider and runtime dispatch tests after generating the BAML client:

```bash
uv run python -m unittest discover -s tests -v
```

### Available Commands

```bash
# Single query
uv run python main.py "What does the fern folder do?"

# Work in a specific directory
uv run python main.py "Find all Python files" --dir /path/to/project

# TUI with specific directory
uv run python main.py "Start" --tui --dir ~/myproject
```

## Whiteboards

_To be added during the session_

## Links

- [Episode Recording](https://www.youtube.com/watch?v=grGSFfyejA0)
- [Source Code](https://github.com/ai-that-works/ai-that-works/tree/main/2025-10-21-agentic-rag-context-engineering)
- [BAML Language](https://github.com/BoundaryML/baml)
- [Discord Community](https://boundaryml.com/discord)

---

## Code Demo: Agent System Built with BAML

An agent system built with BAML that can execute various tools using pattern matching.

## Overview

This project demonstrates an agentic system that:
- Uses BAML to define tool schemas and agent behavior
- Implements tool handlers using Python's `match` statement
- Supports 16 different tool types for file operations, code execution, web fetching, and more

## Architecture

### BAML Components

- **`baml_src/agent-tools.baml`**: Defines all tool types with full descriptions embedded in `@description` annotations
- **`baml_src/agent.baml`**: Defines the agent loop function that decides which tools to call
- **`main.py`**: Python implementation with tool handlers using pattern matching

### Tool Types

The agent supports the following tools:

1. **AgentTool** - Launch recursive sub-agents (fully implemented)
2. **BashTool** - Execute bash commands (fully implemented)
3. **GlobTool** - Find files by glob patterns (fully implemented)
4. **GrepTool** - Search file contents with regex (fully implemented)
5. **LSTool** - List directory contents (fully implemented)
6. **ReadTool** - Read files with line numbers (fully implemented)
7. **EditTool** - Edit files with string replacement (fully implemented)
8. **MultiEditTool** - Multiple edits in one operation (fully implemented)
9. **WriteTool** - Write new files (fully implemented)
10. **NotebookReadTool** - Read Jupyter notebooks (fully implemented)
11. **NotebookEditTool** - Edit Jupyter notebook cells (fully implemented)
12. **WebFetchTool** - Fetch and process web content (requires `requests` + `beautifulsoup4`)
13. **TodoReadTool** - Read todo list (in-memory storage)
14. **TodoWriteTool** - Write todo list (in-memory storage)
15. **WebSearchTool** - Search the web (stub - requires search API)
16. **ExitPlanModeTool** - Exit planning mode

## Tool Handler Pattern

All tools are handled through a single async `execute_tool()` function using Python 3.10+ match statements on the `action` field:

```python
async def execute_tool(tool: types.AgentTools) -> str:
    """Execute a tool based on its type using match statement"""
    match tool.action:
        case "Bash":
            return execute_bash(tool)
        case "Glob":
            return execute_glob(tool)
        case "Agent":
            return await execute_agent(tool)  # Async for recursive calls
        # ... etc for all 16 tools
        case other:
            return f"Unknown tool type: {other}"
```

## Setup

### Prerequisites

- Python 3.10+ (required for match statements)
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)
- Exa API key (set as `EXA_API_KEY` environment variable) - for WebSearch tool

### Installation

```bash
# Install dependencies
uv sync

# Generate BAML client
uv run baml-cli generate
```

### Running

```bash
# Set your API keys
export OPENAI_API_KEY="your-key-here"
export EXA_API_KEY="your-exa-key-here"  # Optional, for WebSearch tool

# Run a single command (uses current directory)
uv run python main.py "What files are in this directory?"

# Interactive mode - keeps asking for commands
uv run python main.py "List files" --interactive

# TUI mode - beautiful text user interface 🎨
uv run python main.py "Start" --tui

# TUI with specific directory
uv run python main.py "Start" --tui --dir ~/myproject

# Specify a working directory (CLI mode)
uv run python main.py "Find all Python files" --dir /path/to/project

# View all options
uv run python main.py --help
```

## User Interfaces

### TUI Mode (Recommended) 🎨

Beautiful text user interface with real-time updates:

```bash
uv run python main.py "Start" --tui
```

Features:
- **Status Bar**: Shows working directory, iteration count, and agent status
- **Main Log**: Pretty-formatted output with panels for tools, results, and agent replies
  - Auto-scrolls to latest content
  - Real-time updates as tools execute
- **Todo Panel**: Live view of the todo list on the right side
- **Input Box**: Command input at the bottom
- **Conversation History**: Maintained across commands for context continuity
- **Responsive UI**: Agent runs in background thread, UI stays snappy
- **Keyboard Shortcuts**: 
  - Enter: Submit command
  - Enter (empty): Continue agent execution after text replies
  - Ctrl+R: Reset conversation history
  - Ctrl+X: Interrupt agent execution
  - Ctrl+C: Quit application

### CLI Modes

**Single Command Mode:**
```bash
uv run python main.py "What files are in this directory?"
```

**Interactive Mode:**
```bash
uv run python main.py "Start" --interactive
```
- Prompts for commands via `input()` after each task
- Type `exit`, `quit`, or `q` to exit
- Ctrl+C returns to prompt instead of exiting

## Agent Loop

The agent loop:
1. Takes a user message
2. Calls the BAML `AgentLoop` function
3. Executes any tools the LLM requests
4. Feeds tool results back to the LLM
5. Repeats until the LLM replies to the user (default max: 999 iterations)

## Key Features

### Type-Safe Tool Calling

BAML generates Pydantic models for all tools, ensuring type safety:

```python
class BashTool(BaseModel):
    action: Literal['Bash']
    command: str
    timeout: Optional[int] = None
    description: Optional[str] = None
```

### Rich Tool Descriptions

Each tool includes its full usage documentation in the `@description` annotation, providing the LLM with comprehensive context about when and how to use each tool.

### Modular Tool Handlers

Each tool has its own handler function that can be tested and maintained independently:

```python
def execute_bash(tool: types.BashTool) -> str:
    """Execute a bash command and return the output"""
    try:
        result = subprocess.run(
            tool.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=tool.timeout / 1000 if tool.timeout else 120,
            cwd=os.getcwd()
        )
        return result.stdout
    except Exception as e:
        return f"Error: {str(e)}"
```

## Dependencies

Core dependencies:
- `baml-py` - BAML Python SDK
- `pydantic` - Data validation
- `typing-extensions` - Type hints support
- `python-dotenv` - Environment variable management
- `textual` - Beautiful TUI framework
- `rich` - Rich text formatting

Optional dependencies for specific tools:
- `requests` + `beautifulsoup4` - For WebFetch tool (install with `uv add requests beautifulsoup4`)
- `exa-py` - For WebSearch tool (install with `uv add exa-py`)
- `ripgrep` (system package) - For Grep tool (usually pre-installed)

## In-Memory State

The agent maintains in-memory state for:
- **Todo list** - Stored in `_todo_store` global variable, persists for the lifetime of the process
- **Agent loop** - Supports recursive sub-agent calls with reduced max iterations

## Sub-Agents

The agent can launch sub-agents to handle focused tasks. Sub-agents use a different BAML function (`SubAgentLoop`) that doesn't include the `AgentTool`, preventing infinite recursion.

**Architecture:**
- Main agent uses `AgentLoop` - has access to all tools including `AgentTool`
- Sub-agents use `SubAgentLoop` - has all tools EXCEPT `AgentTool`
- Sub-agents run in isolated message contexts
- Results are returned to the main agent

In the TUI, sub-agents are visualized with indentation and depth indicators:

```
Iteration 1
🔧 Tool: Glob
✅ Result: [files found]

🔄 Launching Sub-agent (Level 1)
  └─ Sub-agent Iteration 1
    └─ 🔧 Read (1/2)
       ✓ File contents...
    └─ 🔧 Grep (2/2)
       ✓ Matches found...
  ✓ Sub-agent L1 Complete

Iteration 2
...
```

**Visualization Features:**
- Indentation shows nesting level
- Tool progress: `(1/3)` shows current tool of total
- Depth indicator: `[Sub-agent L1]` in status bar
- Compact sub-agent output to reduce visual clutter
- Full interrupt support for sub-agents

**Important Note:** Sub-agents cannot spawn additional sub-agents (by design). The main agent uses `AgentLoop` which includes the `AgentTool`, while sub-agents use `SubAgentLoop` which excludes it. This prevents infinite recursion and keeps sub-agents focused on their specific goals.

## Example Usage

### Command Line

```bash
# Find package.json files
uv run python main.py "What directory contains the file 'package.json'?"

# Work in a specific directory
uv run python main.py "List all JavaScript files" --dir ~/my-project

# Interactive mode for multiple tasks
uv run python main.py "List files" --interactive
```

### Programmatic Usage

```python
# Find package.json files
user_query = 'What directory contains the file "package.json"?'
result = asyncio.run(agent_loop(user_query))
```

The agent will:
1. Use GlobTool to find all `package.json` files
2. Analyze the results
3. Reply to the user with the answer

## Command Line Options

```
usage: main.py [-h] [--dir DIR] [--interactive] [--tui] [--verbose] query

positional arguments:
  query                 The query or task for the agent to perform

options:
  -h, --help            show this help message and exit
  --dir DIR, -d DIR     Working directory for the agent (defaults to current directory)
  --interactive, -i     Run in interactive mode (keep asking for commands)
  --tui, -t            Run in TUI mode (beautiful text user interface)
  --verbose, -v         Enable verbose output
```

**Note**: The agent runs with a very high iteration limit (999) by default, allowing it to complete complex tasks. Sub-agents get a limit of 50 iterations.

## TUI Layout

The TUI provides a beautiful interface with:
- Color-coded tool executions (magenta panels)
- Success results in green panels
- User queries in blue panels
- Live todo list updates on the right
- Real-time status bar at the top

See [TUI_LAYOUT.md](TUI_LAYOUT.md) for a detailed visual layout diagram.

## Project Structure

```
2025-10-21-agentic-rag-context-engineering/
├── baml_src/
│   ├── agent-tools.baml      # Tool type definitions (AgentTools, SubAgentTools)
│   ├── agent.baml             # Agent loop functions (AgentLoop, SubAgentLoop)
│   ├── clients.baml           # LLM client configs
│   └── generators.baml        # Code generation config
├── baml_client/               # Auto-generated BAML client
├── agent_runtime.py           # Shared agent state & execution logic
├── main.py                    # Tool handlers & CLI interface
├── tui.py                     # Beautiful TUI interface
├── ARCHITECTURE.md            # Architecture documentation
├── TUI_LAYOUT.md              # Visual TUI documentation
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

**Key Design:**
- `agent_runtime.py` contains all agent logic (zero duplication)
- Both CLI and TUI use `AgentRuntime` with different callbacks
- Sub-agents use `SubAgentLoop` (no AgentTool access)
- All code is async using `baml_client.async_client`

## Agent Capabilities

BAMMY is a sophisticated AI agent with professional-grade capabilities:

### **Core Features:**
- **File System Operations**: Read, write, edit, and search files
- **Code Analysis**: Understand and manipulate codebases
- **Web Research**: Fetch information and perform web searches
- **Task Management**: Plan, track, and execute complex workflows
- **Bash Execution**: Run system commands and scripts
- **Sub-Agent Delegation**: Delegate complex tasks to focused sub-agents

### **Professional Standards:**
- **Security-First**: Refuses to work on malicious code
- **Convention-Aware**: Follows existing code patterns and standards
- **Efficient Communication**: Concise, direct responses
- **Proactive Task Management**: Uses todo tools extensively
- **Quality Assurance**: Runs lint/typecheck after code changes

### **Technical Details:**
- Uses `gpt-4o-mini` by default (configurable in `agent.baml`)
- Tool handlers include comprehensive error handling
- Supports recursive sub-agent delegation with infinite recursion protection
- Maintains conversation context across iterations
- Some tools (WebSearch, TodoRead/Write) are stubs requiring external services
- The agent loop has a configurable max iteration limit (default: 10)

