from importlib.metadata import PackageNotFoundError, version

from .agent import BaseAgent
from .chain import BaseChain
from .chatllm import BaseChatLLM
from .embedding import BaseEmbedding
from .graph import BaseGraph
from .llm import BaseLLM
from .model import BaseDhtiModel
from .mydi import camel_to_snake, get_di
from .server import BaseServer
from .space import BaseSpace

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

__all__ = [
    "BaseAgent",
    "BaseChain",
    "BaseChatLLM",
    "BaseDhtiModel",
    "BaseEmbedding",
    "BaseGraph",
    "BaseLLM",
    "BaseServer",
    "BaseSpace",
    "camel_to_snake",
    "get_di",
]
