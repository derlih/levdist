"""`levdist` package contains an edit distance functionality.

More information about the algorithm you can find [here](https://en.wikipedia.org/wiki/Levenshtein_distance).
"""

import typing

from ._classic import classic
from ._wagner_fischer import wagner_fischer

if typing.TYPE_CHECKING:
    levenshtein: typing.Callable[[str, str], int]

try:
    from .native import wagner_fischer_native  # type: ignore[import-not-found]

    levenshtein = wagner_fischer_native
except ImportError:
    levenshtein = wagner_fischer

__all__ = ["classic", "levenshtein", "wagner_fischer"]
