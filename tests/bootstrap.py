from kink import di
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

def bootstrap():
    load_dotenv()
    di["main_prompt"] = PromptTemplate.from_template("{input}")
    di["main_llm"] = Ollama(model="phi3", verbose=True, base_url="http://localhost:11434")
    di["function_llm"] = Ollama(model="phi3", verbose=True, base_url="http://localhost:11434")
    di["prefix"] = """
                " You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
    """
    di["suffix"] = "FINAL ANSWER"