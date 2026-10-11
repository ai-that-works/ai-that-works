import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, patch

import httpx
from mcp.client.streamable_http import streamablehttp_client

import main
import parallel_search
from agent_runtime import AgentRuntime, AgentState
from baml_client import types


class ParallelTests(unittest.IsolatedAsyncioTestCase):
    async def test_protocol_requests_and_runtime_loop(self):
        requests = []

        def handle(request):
            requests.append(request)
            payload = json.loads(request.content) if request.content else {}
            method = payload.get("method")
            if method == "initialize":
                result = {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fixture", "version": "1"},
                }
            elif method == "tools/call":
                result = {"content": [{"type": "text", "text": "BAML docs: https://docs.boundaryml.com"}]}
            elif method == "tools/list":
                result = {"tools": [
                    {"name": name, "inputSchema": {"type": "object"}}
                    for name in ("web_search", "web_fetch")
                ]}
            else:
                return httpx.Response(202)
            return httpx.Response(200, json={"jsonrpc": "2.0", "id": payload["id"], "result": result})

        def factory(headers=None, timeout=None, auth=None):
            return httpx.AsyncClient(headers=headers, timeout=timeout, auth=auth, transport=httpx.MockTransport(handle))

        def transport(*args, **kwargs):
            return streamablehttp_client(*args, **kwargs, httpx_client_factory=factory)

        state = AgentState()
        runtime = AgentRuntime(state)
        decisions = [
            types.WebSearchTool(action="WebSearch", query="BAML getting started documentation"),
            types.WebFetchTool(action="WebFetch", url="https://docs.boundaryml.com", prompt="Get started " * 30),
            types.ReplyToUser(action="reply_to_user", message="Found the BAML documentation."),
        ]
        with patch.dict(os.environ, {"WEB_SEARCH_PROVIDER": "parallel"}, clear=True), \
             patch.object(parallel_search, "streamablehttp_client", transport), \
             patch("agent_runtime.b.AgentLoop", AsyncMock(side_effect=decisions)) as model:
            result = await runtime.run_loop("Find BAML docs", max_iterations=3)
        self.assertEqual(result, "Found the BAML documentation.")
        self.assertEqual(model.await_count, 3)
        self.assertIn("https://docs.boundaryml.com", state.messages[-1].message)
        calls = []
        for request in requests:
            self.assertEqual(str(request.url), parallel_search.MCP_URL)
            self.assertEqual(request.headers["user-agent"], parallel_search.USER_AGENT)
            self.assertNotIn("authorization", request.headers)
            payload = json.loads(request.content) if request.content else {}
            if payload.get("method") == "tools/call":
                calls.append(payload["params"])
        self.assertEqual([c["name"] for c in calls], ["web_search", "web_fetch"])
        self.assertEqual(calls[0]["arguments"]["search_queries"], [decisions[0].query])
        self.assertEqual(calls[0]["arguments"]["objective"], decisions[0].query)
        self.assertEqual(calls[1]["arguments"]["urls"], [decisions[1].url])
        self.assertEqual(len(calls[1]["arguments"]["objective"]), 200)
        self.assertEqual([c["arguments"]["session_id"] for c in calls], [state.web_session_id] * 2)
        self.assertNotEqual(AgentState().web_session_id, state.web_session_id)

    async def test_defaults_and_explicit_other_selection(self):
        search = types.WebSearchTool(action="WebSearch", query="BAML")
        fetch = types.WebFetchTool(action="WebFetch", url="https://example.com", prompt="Read")
        for environment in ({}, {"WEB_SEARCH_PROVIDER": "exa"}):
            with patch.dict(os.environ, environment, clear=True), \
                 patch.object(main, "execute_web_search", return_value="Exa result") as exa, \
                 patch.object(main, "execute_web_fetch", return_value="HTML result") as html, \
                 patch.object(parallel_search, "_call_tool", AsyncMock()) as mcp:
                self.assertEqual(await main.execute_tool(search), "Exa result")
                self.assertEqual(await main.execute_tool(fetch), "HTML result")
                exa.assert_called_once_with(search, ".")
                html.assert_called_once_with(fetch, ".")
                mcp.assert_not_awaited()

    async def test_domain_filters_are_explicitly_rejected(self):
        for field in ("allowed_domains", "blocked_domains"):
            tool = types.WebSearchTool(action="WebSearch", query="BAML", **{field: ["example.com"]})
            with patch.object(parallel_search, "_call_tool", AsyncMock()) as call:
                self.assertIn("does not support domain filters", await parallel_search.execute_parallel_tool(tool))
                call.assert_not_awaited()

    async def test_errors_and_timeout(self):
        tool = types.WebSearchTool(action="WebSearch", query="BAML")
        for error, expected in ((RuntimeError("unavailable"), "unavailable"), (asyncio.TimeoutError(), "timed out")):
            with patch.object(parallel_search, "_call_tool", AsyncMock(side_effect=error)):
                self.assertIn(expected, await parallel_search.execute_parallel_tool(tool))

    async def test_mcp_error_result_and_nontext_content(self):
        from mcp.types import CallToolResult, TextContent
        session = AsyncMock()
        session.call_tool.return_value = CallToolResult(
            isError=True, content=[TextContent(type="text", text="Rate limit exceeded")]
        )
        session_context = AsyncMock()
        session_context.__aenter__.return_value = session
        transport_context = AsyncMock()
        transport_context.__aenter__.return_value = (None, None, None)
        with patch.object(parallel_search, "ClientSession", return_value=session_context), \
             patch.object(parallel_search, "streamablehttp_client", return_value=transport_context):
            self.assertEqual(await parallel_search._call_tool("web_search", {}), "Error from Parallel web_search: Rate limit exceeded")
            session.call_tool.return_value = CallToolResult(content=[])
            self.assertEqual(await parallel_search._call_tool("web_search", {}), "No content returned by Parallel.")

    async def test_cancellation_propagates(self):
        started = asyncio.Event()

        async def wait(*args):
            started.set()
            await asyncio.Event().wait()

        tool = types.WebSearchTool(action="WebSearch", query="BAML")
        with patch.object(parallel_search, "_call_tool", wait):
            task = asyncio.create_task(parallel_search.execute_parallel_tool(tool))
            await started.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task


if __name__ == "__main__":
    unittest.main()
