import logging
import sys
from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


class BaseDhtiModel(ABC):
    """A model class to lead the model and tokenizer"""

    model: Any = None

    def __init__(
        self,
        model: Any,
    ) -> None:
        self.model = model

    @classmethod
    @abstractmethod
    def load(cls) -> None:
        if cls.model is None:
            log.info("Loading model")
            t0 = perf_counter()
            # Load the model here
            elapsed = 1000 * (perf_counter() - t0)
            log.info("Model warm-up time: %d ms.", elapsed)
        else:
            log.info("Model is already loaded")

    @classmethod
    @abstractmethod
    def predict(cls, input: Any, **kwargs) -> Any:
        assert input is not None and cls.model is not None  # Sanity check

        # Make sure the model is loaded.
        cls.load()
        t0 = perf_counter()
        # Predict here
        elapsed = 1000 * (perf_counter() - t0)
        log.info("Model prediction time: %d ms.", elapsed)
        return None
