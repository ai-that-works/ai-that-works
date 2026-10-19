"""
Shared agent runtime and state management
"""
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass, field
from uuid import uuid4

from baml_client import types
from baml_client.async_client import b
from baml_py.errors import BamlValidationError
from baml_client.tracing import trace

# Import tool handlers from main
from main import execute_tool as _execute_tool


@dataclass
class AgentState:
    """Shared state for agent execution"""
    messages: list[types.Message] = field(default_factory=list)
    todos: list[types.TodoItem] = field(default_factory=list)
    interrupt_requested: bool = False
    current_iteration: int = 0
    current_depth: int = 0
    working_dir: str = "."
    web_session_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class AgentCallbacks:
    """Callbacks for UI updates during agent execution"""
    on_iteration: Optional[Callable[[int, int], Awaitable[None]]] = None  # (iteration, depth)
    on_tool_start: Optional[Callable[[str, dict, int, int, int], Awaitable[None]]] = None  # (tool_name, params, tool_idx, total_tools, depth)
    on_tool_result: Optional[Callable[[str, int], Awaitable[None]]] = None  # (result, depth)
    on_agent_reply: Optional[Callable[[str], Awaitable[None]]] = None
    on_status_update: Optional[Callable[[str, int], Awaitable[None]]] = None  # (status, iteration)
    on_sub_agent_start: Optional[Callable[[str, str, int], Awaitable[None]]] = None  # (description, prompt, depth)
    on_sub_agent_complete: Optional[Callable[[str, int], Awaitable[None]]] = None  # (result, depth)


class AgentRuntime:
    """Core agent runtime - shared between CLI and TUI"""
    
    def __init__(self, state: AgentState, callbacks: Optional[AgentCallbacks] = None):
        self.state = state
        self.callbacks = callbacks or AgentCallbacks()
    
    # @trace
    async def execute_tool(self, tool: types.AgentTools, depth: int = 0) -> str:
        """Execute a tool, handling sub-agents specially"""
        if tool.action == "Agent":
            return await self.execute_sub_agent(tool, depth)
        else:
            return await _execute_tool(tool, self.state.working_dir, self.state.web_session_id)
    
    # @trace
    async def execute_sub_agent(self, tool: types.AgentTool, parent_depth: int) -> str:
        """
        Execute a sub-agent with its own message context using SubAgentLoop.
        
        Note: SubAgentLoop uses SubAgentTools which excludes AgentTool,
        preventing sub-agents from spawning more sub-agents (infinite recursion protection).
        """
        # Notify UI
        if self.callbacks.on_sub_agent_start:
            await self.callbacks.on_sub_agent_start(tool.description, tool.prompt, parent_depth + 1)
        
        # Create isolated message context for sub-agent
        sub_messages: list[types.Message] = []
        
        # Run sub-agent loop (up to 50 iterations)
        for sub_iteration in range(50):
            if self.state.interrupt_requested:
                return "Sub-agent interrupted by user"
            
            # Update iteration tracking
            if self.callbacks.on_iteration:
                await self.callbacks.on_iteration(sub_iteration + 1, parent_depth + 1)
            
            # Call BAML SubAgentLoop with retry logic for parsing failures
            response = None
            temp_sub_messages = sub_messages.copy()
            max_retries = 3
            
            for retry in range(max_retries):
                try:
                    response = await b.SubAgentLoop(goal=tool.prompt, state=temp_sub_messages, working_dir=self.state.working_dir)
                    break  # Success!
                except BamlValidationError as e:
                    if not e.raw_output.startswith("```json") and not e.raw_output.startswith("{") and not e.raw_output.startswith("["):
                        # Plain text response, treat as reply
                        response = types.ReplyToUser(message=e.raw_output, action="reply_to_user")
                        break
                    else:
                        # Invalid structured response, add error to temp messages and retry
                        temp_sub_messages.append(types.Message(
                            role="assistant",
                            message=f"Returned an invalid response: {e.raw_output}.\n Must be one of the types specified."
                        ))
                        if retry == max_retries - 1:
                            return f"Sub-agent failed to return valid response after {max_retries} attempts"
                except Exception as e:
                    return f"Sub-agent error: {str(e)}"
            
            if response is None:
                return "Sub-agent failed to return a response"
            
            # Check for reply
            if isinstance(response, types.ReplyToUser):
                if self.callbacks.on_sub_agent_complete:
                    await self.callbacks.on_sub_agent_complete(response.message, parent_depth + 1)
                return f"Sub-agent completed:\nTask: {tool.description}\nResult: {response.message}"
            
            # Execute single tool
            if hasattr(response, 'action'):  # It's a tool object
                if self.state.interrupt_requested:
                    return "Sub-agent interrupted by user"
                
                if self.callbacks.on_tool_start:
                    await self.callbacks.on_tool_start(
                        response.action,
                        response.model_dump(exclude={'action'}),
                        1,
                        1,
                        parent_depth + 1
                    )
                
                # Execute tool (sub-agents can't spawn more sub-agents)
                result = await self.execute_tool(response, parent_depth + 1)
                
                if self.callbacks.on_tool_result:
                    await self.callbacks.on_tool_result(result, parent_depth + 1)
                
                # Add tool call with full parameters as assistant message
                tool_params = response.model_dump()
                tool_call_str = f"Tool: {response.action}\n"
                for key, value in tool_params.items():
                    if key != 'action' and value is not None:
                        tool_call_str += f"  {key}: {value}\n"
                sub_messages.append(types.Message(role="assistant", message=tool_call_str))
                
                # Add tool result as assistant message
                sub_messages.append(types.Message(role="assistant", message=result))
        
        return "Sub-agent reached max iterations"
    
    # @trace
    async def run_iteration(self, depth: int = 0) -> tuple[bool, Optional[str]]:
        """
        Run one iteration of the agent loop
        Returns: (is_complete, result_message)
        """
        self.state.current_iteration += 1
        self.state.current_depth = depth
        
        # Check for interrupt
        if self.state.interrupt_requested:
            return (True, "Agent execution interrupted by user")
        
        # Notify UI
        if self.callbacks.on_iteration:
            await self.callbacks.on_iteration(self.state.current_iteration, depth)
        
        # Call BAML agent with retry logic for parsing failures
        if self.callbacks.on_status_update:
            await self.callbacks.on_status_update("Thinking...", self.state.current_iteration)
        
        response = None
        temp_messages = self.state.messages.copy()
        max_retries = 3
        
        for retry in range(max_retries):
            try:
                response = await b.AgentLoop(state=temp_messages, working_dir=self.state.working_dir)
                if isinstance(response, types.ReplyToUser):
                    if response.message.startswith("Tool:"):
                        temp_messages.append(types.Message(role="assistant", message=f"Returned an invalid response: {response.message}.\n Must be one of the types specified."))
                        if retry == max_retries - 1:
                            return (True, f"Agent failed to return valid response after {max_retries} attempts")
                    else:
                        break
                else:
                    break # Success!
            except BamlValidationError as e:
                if not e.raw_output.startswith("```json") and not e.raw_output.startswith("{") and not e.raw_output.startswith("[") and not e.raw_output.startswith("Tool:"):
                    # Plain text response, treat as reply
                    response = types.ReplyToUser(message=e.raw_output, action="reply_to_user")
                    break
                else:
                    # Invalid structured response, add error to temp messages and retry
                    temp_messages.append(types.Message(
                        role="assistant", 
                        message=f"Returned an invalid response: {e.raw_output}.\n Must be one of the types specified."
                    ))
                    if retry == max_retries - 1:
                        return (True, f"Agent failed to return valid response after {max_retries} attempts")
            except Exception as e:
                return (True, f"Error calling agent: {str(e)}")
        
        if response is None:
            return (True, "Agent failed to return a response")
        
        # Check for interrupt
        if self.state.interrupt_requested:
            return (True, "Agent execution interrupted by user")
        
        # Check if agent wants to reply
        if isinstance(response, types.ReplyToUser):
            if self.callbacks.on_agent_reply:
                await self.callbacks.on_agent_reply(response.message)
            return (True, response.message)
        
        # Execute single tool
        if hasattr(response, 'action'):  # It's a tool object
            if self.state.interrupt_requested:
                return (True, "Agent execution interrupted by user")
            
            # Notify UI
            if self.callbacks.on_tool_start:
                await self.callbacks.on_tool_start(
                    response.action,
                    response.model_dump(exclude={'action'}),
                    1,
                    1,
                    depth
                )
            
            if self.callbacks.on_status_update:
                await self.callbacks.on_status_update(
                    f"Executing {response.action}...",
                    self.state.current_iteration
                )
            
            # Execute tool
            result = await self.execute_tool(response, depth)
            
            # Notify UI
            if self.callbacks.on_tool_result:
                await self.callbacks.on_tool_result(result, depth)
            
            # Add tool call with full parameters as assistant message
            tool_params = response.model_dump()
            tool_call_str = f"Tool: {response.action}\n"
            for key, value in tool_params.items():
                if key != 'action' and value is not None:
                    tool_call_str += f"  {key}: {value}\n"
            self.state.messages.append(types.Message(role="assistant", message=tool_call_str))
            
            # Add tool result as assistant message
            self.state.messages.append(types.Message(role="assistant", message=result))
            
            return (False, None)  # Continue iterating
        
        # Unexpected response
        return (True, f"Unexpected response type: {type(response)}")
    
    # @trace
    async def run_loop(self, user_message: str, max_iterations: int = 999, depth: int = 0) -> str:
        """Run the full agent loop until completion"""
        # Add user message (only at depth 0, sub-agents have their own contexts)
        if depth == 0:
            self.state.messages.append(types.Message(role="user", message=user_message))
        
        for _ in range(max_iterations):
            is_complete, result = await self.run_iteration(depth)
            
            if is_complete:
                return result or "Agent completed"
        
        return "Agent reached maximum iterations without completing the task"

