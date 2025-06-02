import pytest
from levdist import LevenshteinFn, classic, levenshtein, wagner_fischer
from levdist._native import wagner_fischer_native

ALL_LEVENSHTEIN_FUNCTION_PYTEST_PARAMS = (
    pytest.param(classic, id="classic"),
    pytest.param(wagner_fischer, id="wagner_fischer"),
    pytest.param(wagner_fischer_native, id="native"),
    pytest.param(levenshtein, id="levenshtein"),
)


@pytest.mark.parametrize(
    ("a", "b", "distance"),
    [
        pytest.param("dog", "dog", 0),
        pytest.param("dog", "", 3),
        pytest.param("", "dog", 3),
        pytest.param("kitten", "sitting", 3),
        pytest.param("sitting", "kitten", 3),
        pytest.param("for", "force", 2),
        pytest.param("Levenshtein", "Frankenstein", 6),
        pytest.param("кошка", "кот", 3, id="Unicode"),
        pytest.param("🏉", "🎻", 1, id="Emoji"),
        pytest.param("🏉", "a", 1, id="Strings with different kind"),
    ],
)
@pytest.mark.parametrize(
    "fn",
    ALL_LEVENSHTEIN_FUNCTION_PYTEST_PARAMS,
)
def test_distance(a: str, b: str, distance: int, fn: LevenshteinFn) -> None:
    assert fn(a, b) == distance
