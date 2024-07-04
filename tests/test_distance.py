from typing import Callable

import pytest

from levenshtein_py import classic, wagner_fischer, wagner_fischer_native


@pytest.mark.parametrize(
    ("a", "b", "distance"),
    [
        pytest.param("dog", "dog", 0),
        pytest.param("dog", "", 3),
        pytest.param("", "dog", 3),
        pytest.param("kitten", "sitting", 3),
        pytest.param("for", "force", 2),
        pytest.param("Levenshtein", "Frankenstein", 6),
    ],
)
@pytest.mark.parametrize("fn", [classic, wagner_fischer, wagner_fischer_native])
def test_distance(a: str, b: str, distance: int, fn: Callable[[str, str], int]):
    assert fn(a, b) == distance