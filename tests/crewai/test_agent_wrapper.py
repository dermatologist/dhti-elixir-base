"""Tests for CrewAI Agent Wrapper."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def dhti_agent():
    """Create a mock BaseAgent instance."""
    from src.dhti_elixir_base import BaseAgent, BaseChatLLM

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Agent response"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        llm = BaseChatLLM(
            base_url="https://api.example.com/chat",
            model="test-model",
            api_key="test-key",
        )

        agent = BaseAgent(
            name="test_agent",
            description="A test agent",
            llm=llm,
            prompt="You are a helpful assistant",
            tools=[],
        )
        yield agent


def test_crewai_agent_wrapper_initialization(dhti_agent):
    """Test that CrewAIAgentWrapper initializes correctly."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAIAgentWrapper

    wrapper = CrewAIAgentWrapper(
        agent=dhti_agent,
        role="Test Agent",
        goal="Test goal",
    )
    assert wrapper is not None
    assert wrapper._dhti_agent == dhti_agent
    assert wrapper.role == "Test Agent"
    assert wrapper.goal == "Test goal"


def test_crewai_agent_wrapper_default_values(dhti_agent):
    """Test that CrewAIAgentWrapper uses default values from agent."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAIAgentWrapper

    wrapper = CrewAIAgentWrapper(agent=dhti_agent)
    assert wrapper is not None
    assert wrapper._dhti_agent == dhti_agent
    assert wrapper.role == dhti_agent.description
    assert "test_agent" in wrapper.goal


def test_crewai_agent_wrapper_execute_task(dhti_agent):
    """Test that CrewAIAgentWrapper can execute tasks."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAIAgentWrapper

    # Mock the agent's get_agent_response method
    with patch.object(dhti_agent, "get_agent_response", return_value="Task completed"):
        wrapper = CrewAIAgentWrapper(agent=dhti_agent)

        # Create a simple task-like object
        task = MagicMock()
        task.description = "Test task"

        result = wrapper.execute_task(task)
        assert result == "Task completed"


def test_crewai_agent_wrapper_string_representation(dhti_agent):
    """Test string representation of the wrapper."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAIAgentWrapper

    wrapper = CrewAIAgentWrapper(agent=dhti_agent)
    str_repr = str(wrapper)
    assert "CrewAIAgentWrapper" in str_repr
    assert "test_agent" in str_repr


def test_crewai_agent_wrapper_with_tools(dhti_agent):
    """Test that CrewAIAgentWrapper can be initialized with tools."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAIAgentWrapper

    mock_tool = MagicMock()
    wrapper = CrewAIAgentWrapper(
        agent=dhti_agent,
        tools=[mock_tool],
    )
    assert wrapper is not None
    assert len(wrapper.tools) > 0
