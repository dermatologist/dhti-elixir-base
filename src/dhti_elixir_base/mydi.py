import re

from kink import di

# Pre-compiled regex for CamelCase to snake_case conversion - avoids recompilation on each call
_CAMEL_TO_SNAKE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case using pre-compiled regex for efficiency."""
    return _CAMEL_TO_SNAKE_PATTERN.sub("_", name).lower()


def get_di(mydi: str, default=None):
    try:
        _module = mydi.split("_", 1)[0]
        _mydi = mydi.split("_", 1)[1]
    except IndexError:
        return di[mydi]
    try:
        return di[_module + "_" + _mydi]
    except KeyError:
        try:
            return di[_mydi]
        except KeyError:
            return default
