"""Tests for CrewAI LangChain Tool Wrapper."""
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def langchain_tool():
    """Create a mock LangChain tool."""
    tool = MagicMock()
    tool.name = "test_tool"
    tool.description = "A test tool"
    tool.run = MagicMock(return_value="Tool result")
    return tool


def test_crewai_langchain_tool_wrapper_initialization(langchain_tool):
    """Test that CrewAILangChainToolWrapper initializes correctly."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    wrapper = CrewAILangChainToolWrapper(langchain_tool=langchain_tool)
    assert wrapper is not None
    assert wrapper._langchain_tool == langchain_tool
    assert wrapper.name == "test_tool"
    assert wrapper.description == "A test tool"


def test_crewai_langchain_tool_wrapper_run_method(langchain_tool):
    """Test that wrapper calls the tool's run method."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    wrapper = CrewAILangChainToolWrapper(langchain_tool=langchain_tool)
    result = wrapper._run("test query")
    
    assert result == "Tool result"
    langchain_tool.run.assert_called_once_with("test query")


def test_crewai_langchain_tool_wrapper_invoke_method():
    """Test that wrapper calls the tool's invoke method if run is not available."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    tool = MagicMock()
    tool.name = "invoke_tool"
    tool.description = "A tool with invoke method"
    tool.invoke = MagicMock(return_value="Invoke result")
    delattr(tool, "run")  # Remove run method to test invoke

    wrapper = CrewAILangChainToolWrapper(langchain_tool=tool)
    result = wrapper._run("test query")
    
    assert result == "Invoke result"
    tool.invoke.assert_called_once_with("test query")


def test_crewai_langchain_tool_wrapper_callable():
    """Test that wrapper works with callable tools."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    tool = MagicMock()
    tool.name = "callable_tool"
    tool.description = "A callable tool"
    tool.__call__ = MagicMock(return_value="Callable result")
    delattr(tool, "run")
    delattr(tool, "invoke")

    wrapper = CrewAILangChainToolWrapper(langchain_tool=tool)
    result = wrapper._run("test query")
    
    assert result == "Callable result"
    tool.__call__.assert_called_once_with("test query")


def test_crewai_langchain_tool_wrapper_with_kwargs(langchain_tool):
    """Test that wrapper passes keyword arguments to the tool."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    wrapper = CrewAILangChainToolWrapper(langchain_tool=langchain_tool)
    result = wrapper._run(query="test query", max_results=5)
    
    assert result == "Tool result"
    langchain_tool.run.assert_called_once_with(query="test query", max_results=5)


def test_crewai_langchain_tool_wrapper_error_handling():
    """Test that wrapper handles errors gracefully."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    tool = MagicMock()
    tool.name = "error_tool"
    tool.description = "A tool that raises errors"
    tool.run = MagicMock(side_effect=Exception("Tool error"))

    wrapper = CrewAILangChainToolWrapper(langchain_tool=tool)
    result = wrapper._run("test query")
    
    assert "Error executing LangChain tool" in result
    assert "Tool error" in result


def test_crewai_langchain_tool_wrapper_string_representation(langchain_tool):
    """Test string representation of the wrapper."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    wrapper = CrewAILangChainToolWrapper(langchain_tool=langchain_tool)
    str_repr = str(wrapper)
    assert "CrewAILangChainToolWrapper" in str_repr
    assert "test_tool" in str_repr


def test_crewai_langchain_tool_wrapper_no_valid_method():
    """Test that wrapper returns error for tools without valid methods."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAILangChainToolWrapper

    tool = MagicMock()
    tool.name = "invalid_tool"
    tool.description = "A tool without valid methods"
    # Remove all invocation methods
    delattr(tool, "run")
    delattr(tool, "invoke")
    tool.__call__ = None

    wrapper = CrewAILangChainToolWrapper(langchain_tool=tool)
    result = wrapper._run("test query")
    
    assert "Error executing LangChain tool" in result
