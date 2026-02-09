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

try:
    from .parlant_agent import ParlantAgent
except ImportError:
    # ParlantAgent requires parlant module which may not be installed

    class ParlantAgent:  # type: ignore[no-redef]
        """
        Placeholder for ParlantAgent when parlant is not installed.

        This class raises an ImportError with installation instructions
        when instantiated without the required 'parlant' extra dependency.

        Raises:
            ImportError: Always raised with installation instructions.
        """

        def __init__(self, *args, **kwargs):  # noqa: ARG002
            """Raise ImportError with installation instructions."""
            msg = (
                "ParlantAgent requires the 'parlant' extra. "
                "Install it with: pip install dhti-elixir-base[parlant]"
            )
            raise ImportError(msg)

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
    "ParlantAgent",
    "camel_to_snake",
    "get_di",
]
