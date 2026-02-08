"""Tests for CrewAI Chain Tool Wrapper."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def dhti_chain():
    """Create a mock BaseChain instance."""
    from src.dhti_elixir_base import BaseChain

    chain = BaseChain()
    # Mock the chain's invoke method
    chain.invoke = MagicMock(return_value={"cards": [{"summary": "Test result"}]})
    yield chain


def test_crewai_chain_tool_wrapper_initialization(dhti_chain):
    """Test that CrewAIChainToolWrapper initializes correctly."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    wrapper = CrewAIChainToolWrapper(
        chain=dhti_chain,
        name="Test Chain Tool",
        description="A test chain tool",
    )
    assert wrapper is not None
    assert wrapper._dhti_chain == dhti_chain
    assert wrapper.name == "Test Chain Tool"
    assert wrapper.description == "A test chain tool"


def test_crewai_chain_tool_wrapper_default_values(dhti_chain):
    """Test that CrewAIChainToolWrapper uses default values from chain."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    wrapper = CrewAIChainToolWrapper(chain=dhti_chain)
    assert wrapper is not None
    assert wrapper._dhti_chain == dhti_chain
    assert "base_chain" in wrapper.name


def test_crewai_chain_tool_wrapper_run_with_kwargs(dhti_chain):
    """Test that CrewAIChainToolWrapper can run with keyword arguments."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    wrapper = CrewAIChainToolWrapper(chain=dhti_chain)
    result = wrapper._run(input="Test input")
    
    assert result is not None
    assert isinstance(result, str)
    dhti_chain.invoke.assert_called_once_with(input="Test input")


def test_crewai_chain_tool_wrapper_run_with_args(dhti_chain):
    """Test that CrewAIChainToolWrapper can run with positional arguments."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    wrapper = CrewAIChainToolWrapper(chain=dhti_chain)
    result = wrapper._run("Test input")
    
    assert result is not None
    assert isinstance(result, str)
    dhti_chain.invoke.assert_called_once_with(input="Test input")


def test_crewai_chain_tool_wrapper_run_no_args():
    """Test that CrewAIChainToolWrapper raises error with no arguments."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base import BaseChain
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    chain = BaseChain()
    wrapper = CrewAIChainToolWrapper(chain=chain)
    
    with pytest.raises(ValueError):
        wrapper._run()


def test_crewai_chain_tool_wrapper_string_representation(dhti_chain):
    """Test string representation of the wrapper."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    wrapper = CrewAIChainToolWrapper(chain=dhti_chain)
    str_repr = str(wrapper)
    assert "CrewAIChainToolWrapper" in str_repr
    assert "base_chain" in str_repr


def test_crewai_chain_tool_wrapper_handles_dict_result(dhti_chain):
    """Test that wrapper handles dictionary results correctly."""
    pytest.importorskip("crewai_tools")
    from src.dhti_elixir_base.crewai import CrewAIChainToolWrapper

    # Test with 'output' key
    dhti_chain.invoke = MagicMock(return_value={"output": "Test output"})
    wrapper = CrewAIChainToolWrapper(chain=dhti_chain)
    result = wrapper._run(input="Test")
    assert "Test output" in result

    # Test with 'cards' key
    dhti_chain.invoke = MagicMock(return_value={"cards": [{"summary": "Card summary"}]})
    wrapper = CrewAIChainToolWrapper(chain=dhti_chain)
    result = wrapper._run(input="Test")
    assert "summary" in result
