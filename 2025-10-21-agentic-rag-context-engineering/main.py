import asyncio
import subprocess
import os
import glob as glob_module
import fnmatch
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from baml_client import types

# In-memory storage for todos
_todo_store: list[types.TodoItem] = []


def execute_bash(tool: types.BashTool, working_dir: str = ".") -> str:
    """Execute a bash command and return the output"""
    try:
        result = subprocess.run(
            tool.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=tool.timeout / 1000 if tool.timeout else 120,  # Convert ms to seconds
            cwd=working_dir
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}"
            
        return output if output else "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {tool.timeout}ms"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def execute_glob(tool: types.GlobTool, working_dir: str = ".") -> str:
    """Find files matching a glob pattern"""
    try:
        search_path = tool.path if tool.path else working_dir
        pattern = os.path.join(search_path, tool.pattern) if not tool.pattern.startswith("**/") else tool.pattern
        
        matches = glob_module.glob(pattern, recursive=True)
        
        if not matches:
            return f"No files found matching pattern: {tool.pattern}"
        
        # Sort by modification time
        matches.sort(key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        
        # Normalize paths to be relative to working_dir
        working_dir_path = Path(working_dir).resolve()
        normalized_matches = []
        for match in matches[:50]:  # Limit to first 50 matches
            try:
                match_path = Path(match).resolve()
                # Try to make it relative to working_dir
                try:
                    relative_path = match_path.relative_to(working_dir_path)
                    normalized_matches.append(str(relative_path))
                except ValueError:
                    # If it can't be made relative, use the absolute path
                    normalized_matches.append(match)
            except Exception:
                # If there's any issue, just use the original path
                normalized_matches.append(match)
        
        return "\n".join(normalized_matches)
    except Exception as e:
        return f"Error executing glob: {str(e)}"


def execute_grep(tool: types.GrepTool, working_dir: str = ".") -> str:
    """Search for pattern in files"""
    try:
        search_path = tool.path if tool.path else working_dir
        
        # Build rg command
        cmd = ["rg", tool.pattern, search_path, "--files-with-matches"]
        
        if tool.include:
            cmd.extend(["--glob", tool.include])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            files = result.stdout.strip().split("\n")
            
            # Normalize paths to be relative to working_dir
            working_dir_path = Path(working_dir).resolve()
            normalized_files = []
            for file in files[:50]:  # Limit to first 50 matches
                try:
                    file_path = Path(file).resolve()
                    # Try to make it relative to working_dir
                    try:
                        relative_path = file_path.relative_to(working_dir_path)
                        normalized_files.append(str(relative_path))
                    except ValueError:
                        # If it can't be made relative, use the absolute path
                        normalized_files.append(file)
                except Exception:
                    # If there's any issue, just use the original path
                    normalized_files.append(file)
            
            return "\n".join(normalized_files)
        elif result.returncode == 1:
            return f"No matches found for pattern: {tool.pattern}"
        else:
            return f"Error: {result.stderr}"
    except FileNotFoundError:
        # Fallback to Python's re if rg is not available
        return "Error: ripgrep (rg) not found. Please install ripgrep."
    except Exception as e:
        return f"Error executing grep: {str(e)}"


def execute_ls(tool: types.LSTool, working_dir: str = ".") -> str:
    """List files in a directory"""
    try:
        path = Path(tool.path) if tool.path else Path(working_dir)
        
        if not path.exists():
            return f"Directory not found: {tool.path}"
        
        if not path.is_dir():
            return f"Not a directory: {tool.path}"
        
        items = []
        for item in path.iterdir():
            # Skip ignored patterns
            if tool.ignore:
                skip = False
                for pattern in tool.ignore:
                    if fnmatch.fnmatch(item.name, pattern):
                        skip = True
                        break
                if skip:
                    continue
            
            item_type = "DIR " if item.is_dir() else "FILE"
            items.append(f"{item_type} {item.name}")
        
        items.sort()
        return "\n".join(items) if items else "Empty directory"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def execute_read(tool: types.ReadTool, working_dir: str = ".") -> str:
    """Read a file"""
    try:
        # If file_path is relative, make it relative to working_dir
        if not os.path.isabs(tool.file_path):
            path = Path(working_dir) / tool.file_path
        else:
            path = Path(tool.file_path)
        
        if not path.exists():
            return f"File not found: {tool.file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        start = tool.offset if tool.offset else 0
        end = start + tool.limit if tool.limit else len(lines)
        
        # Limit to 5000 lines per read
        max_lines = 5000
        if end - start > max_lines:
            end = start + max_lines
        
        result_lines = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            # Truncate very long lines at 20k characters
            if len(line) > 20000:
                line = line[:20000] + "... [line truncated at 20k characters]\n"
            result_lines.append(f"{i:6d}|{line.rstrip()}")
        
        # Add truncation notice if we hit the limit
        if end < total_lines:
            remaining = total_lines - end
            truncation_notice = f"\n\n... [Output truncated: showing lines {start + 1}-{end} of {total_lines} total lines ({remaining} lines remaining)]\n"
            truncation_notice += f"To read more, use the Read tool with: offset={end}, limit={min(5000, remaining)}"
            result_lines.append(truncation_notice)
        
        return "\n".join(result_lines) if result_lines else "Empty file"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def execute_edit(tool: types.EditTool, working_dir: str = ".") -> str:
    """Edit a file"""
    try:
        # If file_path is relative, make it relative to working_dir
        if not os.path.isabs(tool.file_path):
            path = Path(working_dir) / tool.file_path
        else:
            path = Path(tool.file_path)
        
        if not path.exists():
            return f"File not found: {tool.file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if tool.replace_all:
            new_content = content.replace(tool.old_string, tool.new_string)
            count = content.count(tool.old_string)
        else:
            if content.count(tool.old_string) > 1:
                return f"Error: old_string is not unique in file (found {content.count(tool.old_string)} occurrences)"
            new_content = content.replace(tool.old_string, tool.new_string, 1)
            count = 1 if tool.old_string in content else 0
        
        if count == 0:
            return "Error: old_string not found in file"
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"Successfully edited {tool.file_path} ({count} replacement(s))"
    except Exception as e:
        return f"Error editing file: {str(e)}"


def execute_multi_edit(tool: types.MultiEditTool, working_dir: str = ".") -> str:
    """Edit a file with multiple edits"""
    try:
        # If file_path is relative, make it relative to working_dir
        if not os.path.isabs(tool.file_path):
            path = Path(working_dir) / tool.file_path
        else:
            path = Path(tool.file_path)
        
        if not path.exists():
            return f"File not found: {tool.file_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply edits sequentially
        for i, edit in enumerate(tool.edits):
            if edit.replace_all:
                content = content.replace(edit.old_string, edit.new_string)
            else:
                if content.count(edit.old_string) > 1:
                    return f"Error in edit {i+1}: old_string is not unique (found {content.count(edit.old_string)} occurrences)"
                if edit.old_string not in content:
                    return f"Error in edit {i+1}: old_string not found"
                content = content.replace(edit.old_string, edit.new_string, 1)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully applied {len(tool.edits)} edits to {tool.file_path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"


def execute_write(tool: types.WriteTool, working_dir: str = ".") -> str:
    """Write a file"""
    try:
        # If file_path is relative, make it relative to working_dir
        if not os.path.isabs(tool.file_path):
            path = Path(working_dir) / tool.file_path
        else:
            path = Path(tool.file_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(tool.content)
        
        return f"Successfully wrote {tool.file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def execute_notebook_read(tool: types.NotebookReadTool, working_dir: str = ".") -> str:
    """Read a Jupyter notebook"""
    try:
        import json
        # If notebook_path is relative, make it relative to working_dir
        if not os.path.isabs(tool.notebook_path):
            path = Path(working_dir) / tool.notebook_path
        else:
            path = Path(tool.notebook_path)
        
        if not path.exists():
            return f"Notebook not found: {tool.notebook_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells_output = []
        for i, cell in enumerate(notebook.get('cells', [])):
            cell_type = cell.get('cell_type', 'unknown')
            source = ''.join(cell.get('source', []))
            cells_output.append(f"Cell {i} ({cell_type}):\n{source}\n")
        
        return "\n".join(cells_output) if cells_output else "Empty notebook"
    except Exception as e:
        return f"Error reading notebook: {str(e)}"


def execute_notebook_edit(tool: types.NotebookEditTool, working_dir: str = ".") -> str:
    """Edit a Jupyter notebook cell"""
    try:
        import json
        # If notebook_path is relative, make it relative to working_dir
        if not os.path.isabs(tool.notebook_path):
            path = Path(working_dir) / tool.notebook_path
        else:
            path = Path(tool.notebook_path)
        
        if not path.exists():
            return f"Notebook not found: {tool.notebook_path}"
        
        with open(path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells = notebook.get('cells', [])
        
        if tool.edit_mode == "delete":
            if 0 <= tool.cell_number < len(cells):
                cells.pop(tool.cell_number)
            else:
                return f"Error: cell index {tool.cell_number} out of range"
        elif tool.edit_mode == "insert":
            if not tool.cell_type:
                return "Error: cell_type is required for insert mode"
            new_cell = {
                'cell_type': tool.cell_type,
                'source': tool.new_source.split('\n'),
                'metadata': {}
            }
            cells.insert(tool.cell_number, new_cell)
        else:  # replace
            if 0 <= tool.cell_number < len(cells):
                cells[tool.cell_number]['source'] = tool.new_source.split('\n')
                if tool.cell_type:
                    cells[tool.cell_number]['cell_type'] = tool.cell_type
            else:
                return f"Error: cell index {tool.cell_number} out of range"
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        return f"Successfully edited notebook {tool.notebook_path}"
    except Exception as e:
        return f"Error editing notebook: {str(e)}"


def execute_web_fetch(tool: types.WebFetchTool, working_dir: str = ".") -> str:
    """Fetch and process web content"""
    try:
        import requests  # type: ignore
        from bs4 import BeautifulSoup  # type: ignore
        
        response = requests.get(tool.url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Simple markdown conversion (just cleaning up whitespace)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        markdown_content = '\n'.join(lines)

        # TODO: call haiku to summarize the content given the query and how its related.
        
        # Truncate if too long
        truncation_message = ""
        if len(markdown_content) > 10000:
            markdown_content = markdown_content[:10000] + "\n... [truncated]"
            truncation_message = "if you need more information, call the WebFetch tool again to get the rest of the content with a file path"
        
        return f"Content from {tool.url}:\n\n{markdown_content}\n\nUser prompt: {tool.prompt}\n\n{truncation_message}".strip()
    except ImportError:
        return "Error: requests and beautifulsoup4 packages are required for web fetching. Install with: pip install requests beautifulsoup4"
    except Exception as e:
        return f"Error fetching web content: {str(e)}"


def execute_todo_read(tool: types.TodoReadTool, working_dir: str = ".") -> str:
    """Read the todo list from in-memory storage"""
    global _todo_store
    
    if not _todo_store:
        return "No todos currently tracked"
    
    todo_summary = []
    for todo in _todo_store:
        status_icon = "✓" if todo.status == "completed" else "→" if todo.status == "in_progress" else "○"
        todo_summary.append(f"{status_icon} [{todo.priority}] {todo.content} (id: {todo.id}, status: {todo.status})")
    
    return f"Current todos ({len(_todo_store)}):\n" + "\n".join(todo_summary)


def execute_todo_write(tool: types.TodoWriteTool, working_dir: str = ".") -> str:
    """Write the todo list to in-memory storage"""
    global _todo_store
    
    # Replace entire todo list with new one
    _todo_store = tool.todos
    
    todo_summary = []
    for todo in tool.todos:
        status_icon = "✓" if todo.status == "completed" else "→" if todo.status == "in_progress" else "○"
        todo_summary.append(f"{status_icon} [{todo.priority}] {todo.content} (id: {todo.id})")
    
    return f"Updated {len(tool.todos)} todos:\n" + "\n".join(todo_summary)


def execute_web_search(tool: types.WebSearchTool, working_dir: str = ".") -> str:
    """Search the web using Exa, the fastest and most accurate web search API for AI."""
    try:
        import os
        from exa_py import Exa
        
        # Get API key from environment
        api_key = os.getenv("EXA_API_KEY")
        if not api_key:
            return "Error: EXA_API_KEY environment variable not set. Please set your Exa API key."
        
        # Initialize Exa client
        exa = Exa(api_key=api_key)
        
        # Build search parameters
        search_params = {
            "query": tool.query,
            "num_results": 5,  # Limit to 5 results for token efficiency
            "text": True,  # Get the content
            "type": "auto",  # Let Exa determine the best search type
        }
        
        # Perform search with content
        search_response = exa.search_and_contents(**search_params)
        
        if not search_response.results:
            return f"No results found for query: '{tool.query}'"
        
        # Format results
        results = []
        for i, result in enumerate(search_response.results, 1):
            title = result.title or "No title"
            url = result.url
            text = result.text or "No content available"
            
            # Truncate text if too long
            if len(text) > 500:
                text = text[:500] + "..."
            
            results.append(f"{i}. **{title}**\n   URL: {url}\n   Content: {text}\n")
        
        return f"Web search results for '{tool.query}':\n\n" + "\n".join(results)
        
    except ImportError:
        return "Error: exa-py package not installed. Run 'uv add exa-py' to install it."
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def execute_exit_plan_mode(tool: types.ExitPlanModeTool, working_dir: str = ".") -> str:
    """Exit plan mode"""
    return f"Plan presented to user:\n{tool.plan}\n\nWaiting for user approval..."


async def execute_agent(tool: types.AgentTool) -> str:
    """Launch a sub-agent (recursive call)"""
    try:
        print(f"\n🔄 Launching sub-agent: {tool.description}")
        print(f"   Prompt: {tool.prompt[:100]}{'...' if len(tool.prompt) > 100 else ''}")
        
        # Recursively call the agent loop with a reasonable limit for sub-agents
        result = await agent_loop(tool.prompt, max_iterations=50, working_dir=".")
        
        return f"Sub-agent completed:\nTask: {tool.description}\nResult: {result}"
    except Exception as e:
        return f"Sub-agent error: {str(e)}"


async def execute_tool(tool: types.AgentTools, working_dir: str = ".") -> str:
    """Execute a tool based on its type using match statement"""
    match tool.action:
        case "Bash":
            return execute_bash(tool, working_dir)
        case "Glob":
            return execute_glob(tool, working_dir)
        case "Grep":
            return execute_grep(tool, working_dir)
        case "LS":
            return execute_ls(tool, working_dir)
        case "Read":
            return execute_read(tool, working_dir)
        case "Edit":
            return execute_edit(tool, working_dir)
        case "MultiEdit":
            return execute_multi_edit(tool, working_dir)
        case "Write":
            return execute_write(tool, working_dir)
        case "NotebookRead":
            return execute_notebook_read(tool, working_dir)
        case "NotebookEdit":
            return execute_notebook_edit(tool, working_dir)
        case "WebFetch":
            return execute_web_fetch(tool, working_dir)
        case "TodoRead":
            return execute_todo_read(tool, working_dir)
        case "TodoWrite":
            return execute_todo_write(tool, working_dir)
        case "WebSearch":
            return execute_web_search(tool, working_dir)
        case "ExitPlanMode":
            return execute_exit_plan_mode(tool, working_dir)
        case "Agent":
            return await execute_agent(tool)
        case other:
            return f"Unknown tool type: {other}"


async def agent_loop(user_message: str, max_iterations: int = 999, working_dir: str = ".") -> str:
    """Main agent loop that calls the BAML agent and executes tools"""
    from agent_runtime import AgentState, AgentCallbacks, AgentRuntime
    import os
    
    # Suppress BAML verbose logging for CLI
    os.environ["BAML_LOG"] = "WARN"
    
    # Create state and callbacks for CLI
    state = AgentState(working_dir=working_dir)
    
    async def on_reply(msg: str) -> None:
        print(f"\n🤖 Agent reply: {msg}")
    
    callbacks = AgentCallbacks(
        on_iteration=print_iteration,
        on_tool_start=print_tool_start,
        on_tool_result=print_tool_result,
        on_agent_reply=on_reply,
    )
    
    runtime = AgentRuntime(state, callbacks)
    return await runtime.run_loop(user_message, max_iterations=max_iterations, depth=0)


async def print_iteration(iteration: int, depth: int) -> None:
    """Print iteration info"""
    if depth == 0:
        print(f"\n{'='*60}")
        print(f"Iteration {iteration}")
        print(f"{'='*60}")


async def print_tool_start(tool_name: str, params: dict, tool_idx: int, total_tools: int, depth: int) -> None:
    """Print tool execution start"""
    if depth == 0:
        print(f"\n🔧 Executing tool: {tool_name}")
        if params:
            # Show only essential parameters, not the full dict
            essential_params = {}
            for key, value in params.items():
                if key in ['file_path', 'pattern', 'command', 'path']:
                    essential_params[key] = value
            if essential_params:
                print(f"   Parameters: {essential_params}")


async def print_tool_result(result: str, depth: int) -> None:
    """Print tool result"""
    if depth == 0:
        # Truncate long results for CLI
        if len(result) > 500:
            result = result[:500] + f"\n... [truncated: showing first 500 of {len(result)} characters]"
        print(f"   Result: {result}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="BAMMY Agent - Agentic RAG Context Engineering Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a single command
  python main.py "What files are in this directory?"
  
  # Interactive mode - keeps asking for commands
  python main.py --interactive
  
  # TUI mode - beautiful text interface (no initial query needed)
  python main.py --tui
  
  # TUI mode with initial query
  python main.py "List files" --tui
  
  # Specify a working directory
  python main.py "Find all Python files" --dir /path/to/project
        """
    )
    
    parser.add_argument(
        "query",
        type=str,
        nargs="?",
        default=None,
        help="The query or task for the agent to perform (optional in TUI mode)"
    )
    
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        default=None,
        help="Working directory for the agent (defaults to current directory)"
    )
    
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode (keep asking for commands)"
    )
    
    parser.add_argument(
        "--tui",
        "-t",
        action="store_true",
        help="Run in TUI mode (beautiful text user interface)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Launch TUI mode if requested
    if args.tui:
        from tui import run_tui
        
        work_dir = None
        if args.dir:
            work_dir = Path(args.dir).resolve()
            if not work_dir.exists():
                print(f"❌ Error: Directory does not exist: {work_dir}")
                sys.exit(1)
            if not work_dir.is_dir():
                print(f"❌ Error: Not a directory: {work_dir}")
                sys.exit(1)
            work_dir = str(work_dir)
        
        run_tui(working_dir=work_dir, initial_query=args.query)
        return
    
    # Set working directory for CLI mode
    if args.dir:
        work_dir = str(Path(args.dir).resolve())
        work_dir_path = Path(work_dir)
        if not work_dir_path.exists():
            print(f"❌ Error: Directory does not exist: {work_dir}")
            sys.exit(1)
        if not work_dir_path.is_dir():
            print(f"❌ Error: Not a directory: {work_dir}")
            sys.exit(1)
        
        os.chdir(work_dir)
        print(f"📁 Working directory: {work_dir}")
    else:
        work_dir = os.getcwd()
        print(f"📁 Working directory: {work_dir}")
    
    # Require query in non-interactive/non-TUI mode
    if not args.query and not args.interactive:
        parser.error("query is required unless using --interactive mode")
    
    # Print header
    print("🤖 BAMMY Agent - Agentic RAG Context Engineering Demo")
    print("=" * 60)
    
    # Interactive loop or single command
    first_query = args.query
    
    while True:
        try:
            if first_query:
                query = first_query
                first_query = None  # Only use the first query once
            else:
                print("\n" + "=" * 60)
                query = input("📝 Enter your command (or 'exit' to quit): ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break
            
            print(f"\n📝 Query: {query}")
            print("🔄 Running agent (no iteration limit)...")
            print("=" * 60)
            
            # Run the agent with no iteration limit
            result = asyncio.run(agent_loop(query, max_iterations=999, working_dir=work_dir))
            
            print(f"\n{'='*60}")
            print(f"✅ Final result:\n{result}")
            print(f"{'='*60}")
            
            # If not in interactive mode, exit after first query
            if not args.interactive:
                break
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            if args.interactive:
                continue  # Go back to prompt
            else:
                sys.exit(130)
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            if not args.interactive:
                sys.exit(1)
            # In interactive mode, continue to next query


if __name__ == "__main__":
    load_dotenv()
    print(os.getenv("BOUNDARY_API_KEY"))
    main()
