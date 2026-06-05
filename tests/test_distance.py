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


@pytest.mark.parametrize(
    ("a", "b", "distance"),
    [
        pytest.param(b"dog", b"dog", 0),
        pytest.param(b"dog", b"", 3),
        pytest.param(b"", b"dog", 3),
        pytest.param(b"kitten", b"sitting", 3),
        pytest.param(b"sitting", b"kitten", 3),
        pytest.param(b"for", b"force", 2),
        pytest.param(b"\xff\xfe\xfd", b"\xff\xfe", 1, id="High bytes"),
    ],
)
@pytest.mark.parametrize(
    "fn",
    ALL_LEVENSHTEIN_FUNCTION_PYTEST_PARAMS,
)
def test_distance_bytes(a: bytes, b: bytes, distance: int, fn: LevenshteinFn) -> None:
    assert fn(a, b) == distance


@pytest.mark.parametrize(
    ("a", "b", "distance"),
    [
        pytest.param("dog", b"dog", 0, id="str-bytes same ASCII"),
        pytest.param(b"dog", "dog", 0, id="bytes-str same ASCII"),
        pytest.param("", b"dog", 3, id="empty str vs bytes"),
        pytest.param(b"", "dog", 3, id="empty bytes vs str"),
        pytest.param("kitten", b"sitting", 3, id="str-bytes classic example"),
        pytest.param(b"kitten", "sitting", 3, id="bytes-str classic example"),
        pytest.param("for", b"force", 2, id="str-bytes prefix"),
    ],
)
@pytest.mark.parametrize(
    "fn",
    ALL_LEVENSHTEIN_FUNCTION_PYTEST_PARAMS,
)
def test_distance_mixed(
    a: str | bytes,
    b: str | bytes,
    distance: int,
    fn: LevenshteinFn,
) -> None:
    assert fn(a, b) == distance
