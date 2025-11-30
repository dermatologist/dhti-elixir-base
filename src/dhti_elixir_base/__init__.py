import sys

from .agent import BaseAgent
from .chain import BaseChain
from .embedding import BaseEmbedding
from .graph import BaseGraph
from .llm import BaseLLM
from .model import BaseDhtiModel
from .mydi import get_di
from .server import BaseServer
from .space import BaseSpace

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

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
    "BaseDhtiModel",
    "BaseEmbedding",
    "BaseGraph",
    "BaseLLM",
    "BaseServer",
    "BaseSpace",
    "get_di",
]
