"""`levdist` package contains an edit distance functionality.

More information about the algorithm you can find [here](https://en.wikipedia.org/wiki/Levenshtein_distance).
"""

import typing

from ._classic import classic
from ._wagner_fischer import wagner_fischer

LevenshteinFn = typing.Callable[[str, str], int]

if typing.TYPE_CHECKING:
    levenshtein: LevenshteinFn

try:
    from ._native import wagner_fischer_native

    levenshtein = wagner_fischer_native
except ImportError:
    levenshtein = wagner_fischer

__all__ = ["LevenshteinFn", "classic", "levenshtein", "wagner_fischer"]
