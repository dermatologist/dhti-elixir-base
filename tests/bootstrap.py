from kink import di
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

def bootstrap():
    load_dotenv()
    di["main_prompt"] = PromptTemplate.from_template("{input}")
    di["main_llm"] = Ollama(model="phi3", verbose=True, base_url="http://localhost:11434")