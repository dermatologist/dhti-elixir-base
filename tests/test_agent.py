import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(scope="session")
def agent():
    from src.dhti_elixir_base import BaseAgent

    return BaseAgent()


def test_agent_response(agent, capsys):
    input_data = {"input": "Answer in one word: What is the capital of France?"}
    _agent = agent.get_agent_response(context=input_data["input"])
    print(_agent)
    captured = capsys.readouterr()
    assert "processing your request" in captured.out


def test_base_agent(agent, capsys):
    o = agent.name
    print("Agent name: ", o)
    captured = capsys.readouterr()
    assert "Agent name:  base_agent" in captured.out


def test_base_agent_accepts_legacy_mcp_config():
    from src.dhti_elixir_base import BaseAgent

    custom_agent = BaseAgent(
        mcp={
            "test": {
                "transport": "http",
                "url": "http://localhost:9000/mcp",
            }
        }
    )
    assert custom_agent.client is not None


def test_has_tool_runs_async_lookup_from_sync_context(agent):
    with patch.object(agent.client, "list_tools", new_callable=AsyncMock) as list_tools:
        list_tools.return_value = [object()]

        assert agent.has_tool() is True


def test_has_tool_raises_guidance_in_async_context(agent):
    async def call_sync_method():
        agent.has_tool()

    with pytest.raises(RuntimeError, match="Use ahas_tool\(\) instead"):
        asyncio.run(call_sync_method())


def test_ahas_tool_runs_in_async_context(agent):
    with patch.object(agent.client, "list_tools", new_callable=AsyncMock) as list_tools:
        list_tools.return_value = [object()]

        assert asyncio.run(agent.ahas_tool()) is True


def test_get_agent_response_runs_async_agent_from_sync_context(agent):
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={"messages": [SimpleNamespace(content="test response")]}
    )

    with (
        patch("src.dhti_elixir_base.agent.create_agent", return_value=mock_agent),
        patch.object(
            agent.client, "list_tools", new_callable=AsyncMock, return_value=[]
        ),
    ):
        assert agent.get_agent_response("test query") == "test response"


def test_get_agent_response_raises_guidance_in_async_context(agent):
    async def call_sync_method():
        agent.get_agent_response("test query")

    with pytest.raises(RuntimeError, match="Use aget_agent_response\(\) instead"):
        asyncio.run(call_sync_method())


def test_aget_agent_response_runs_in_async_context(agent):
    mock_agent = MagicMock()
    mock_agent.ainvoke = AsyncMock(
        return_value={"messages": [SimpleNamespace(content="async response")]}
    )

    with (
        patch("src.dhti_elixir_base.agent.create_agent", return_value=mock_agent),
        patch.object(
            agent.client, "list_tools", new_callable=AsyncMock, return_value=[]
        ),
    ):
        assert asyncio.run(agent.aget_agent_response("test query")) == "async response"
