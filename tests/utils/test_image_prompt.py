# Unit tests for image_prompt.py
import pytest

from src.dhti_elixir_base.utils.image_prompt import image_prompt


def test_image_prompt_returns_chatprompttemplate():
    tpl = image_prompt(
        encoded_image_url="data:image/png;base64,abc123",
        input_prompt="Describe the image.",
        system_prompt="You are a helpful assistant.",
    )
    # Should be a ChatPromptTemplate
    from langchain_core.prompts import ChatPromptTemplate

    assert isinstance(tpl, ChatPromptTemplate)


def test_image_prompt_structure():
    tpl = image_prompt(
        encoded_image_url="data:image/png;base64,abc123",
        input_prompt="Describe the image.",
        system_prompt="System instructions.",
    )
    # Inspect the ChatPromptTemplate's message structure
    # The first message should be a SystemMessagePromptTemplate with the correct template
    system_msg = tpl.messages[0]
    assert hasattr(system_msg, "prompt")
    assert system_msg.prompt.template == "{system_prompt}"

    # The second message should be a HumanMessagePromptTemplate
    human = tpl.messages[1]
    from langchain_core.prompts import HumanMessagePromptTemplate

    assert isinstance(human, HumanMessagePromptTemplate)
    # The prompt attribute should be a list of templates
    templates = human.prompt
    from langchain_core.prompts.image import ImagePromptTemplate
    from langchain_core.prompts.prompt import PromptTemplate

    assert any(
        isinstance(t, PromptTemplate) and t.template == "{input_prompt}"
        for t in templates
    )
    assert any(
        isinstance(t, ImagePromptTemplate)
        and t.template == {"url": "{encoded_image_url}"}
        for t in templates
    )
