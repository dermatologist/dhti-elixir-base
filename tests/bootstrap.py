from dotenv import load_dotenv
from kink import di
from langchain_core.language_models.fake import FakeListLLM
from langchain_core.prompts import PromptTemplate


def bootstrap():
    load_dotenv()
    di["main_prompt"] = PromptTemplate.from_template("{input}")
    fake_llm = FakeListLLM(responses=["Paris", "Paris", "Paris"])
    di["main_llm"] = fake_llm
    di["clinical_llm"] = fake_llm
    di["function_llm"] = fake_llm
    di["grounding_llm"] = fake_llm
    di["prefix"] = """
                " You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
    """
    di["suffix"] = "FINAL ANSWER"
