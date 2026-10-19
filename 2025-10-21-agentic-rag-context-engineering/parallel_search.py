"""Anonymous web tools over Parallel's Streamable HTTP MCP endpoint."""
import asyncio
from datetime import timedelta
from uuid import uuid4

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = "https://search.parallel.ai/mcp"
USER_AGENT = "ai-that-works/agentic-rag (+https://github.com/ai-that-works/ai-that-works)"
_DIRECT_SESSION_ID = str(uuid4())


def _error_message(exc: Exception) -> str:
    nested = getattr(exc, "exceptions", None)
    if nested:
        return "; ".join(_error_message(error) for error in nested)
    return str(exc)


async def _call_tool(name: str, arguments: dict) -> str:
    async with streamablehttp_client(
        MCP_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
        sse_read_timeout=60,
    ) as (read, write, _):
        async with ClientSession(
            read, write, read_timeout_seconds=timedelta(seconds=30)
        ) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            text = "\n".join(
                block.text for block in result.content if block.type == "text"
            )
            if result.isError:
                return f"Error from Parallel {name}: {text}"
            return text or "No content returned by Parallel."


async def execute_parallel_tool(tool, session_id: str | None = None) -> str:
    if tool.action == "WebSearch":
        if tool.allowed_domains or tool.blocked_domains:
            return "Error: Parallel's anonymous MCP does not support domain filters."
        name = "web_search"
        arguments = {"objective": tool.query, "search_queries": [tool.query]}
    else:
        name = "web_fetch"
        arguments = {"urls": [tool.url], "objective": tool.prompt[:200]}
    arguments["session_id"] = session_id or _DIRECT_SESSION_ID
    try:
        return await asyncio.wait_for(_call_tool(name, arguments), timeout=60)
    except asyncio.TimeoutError:
        return "Error: Parallel MCP request timed out."
    except Exception as exc:
        return f"Error calling Parallel MCP: {_error_message(exc)}"
