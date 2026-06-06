import pytest
from levdist import LevenshteinFn, classic, levenshtein, wagner_fischer
from levdist._native import wagner_fischer_native


@pytest.mark.parametrize(
    ("a", "b", "distance"),
    [
        pytest.param("dog", "dog", 0, id="str-identical"),
        pytest.param("dog", "", 3, id="str-to-empty"),
        pytest.param("", "dog", 3, id="empty-to-str"),
        pytest.param("kitten", "sitting", 3, id="kitten-sitting"),
        pytest.param("sitting", "kitten", 3, id="sitting-kitten"),
        pytest.param("for", "force", 2, id="str-prefix"),
        pytest.param("Levenshtein", "Frankenstein", 6, id="levenshtein-frankenstein"),
        pytest.param("кошка", "кот", 3, id="unicode"),
        pytest.param("🏉", "🎻", 1, id="emoji"),
        pytest.param("🏉", "a", 1, id="emoji-vs-ascii"),
        pytest.param(b"dog", b"dog", 0, id="bytes-identical"),
        pytest.param(b"dog", b"", 3, id="bytes-to-empty"),
        pytest.param(b"", b"dog", 3, id="empty-to-bytes"),
        pytest.param(b"kitten", b"sitting", 3, id="bytes-kitten-sitting"),
        pytest.param(b"sitting", b"kitten", 3, id="bytes-sitting-kitten"),
        pytest.param(b"for", b"force", 2, id="bytes-prefix"),
        pytest.param(b"\xff\xfe\xfd", b"\xff\xfe", 1, id="high-bytes"),
        pytest.param("dog", b"dog", 0, id="str-bytes-identical"),
        pytest.param(b"dog", "dog", 0, id="bytes-str-identical"),
        pytest.param("", b"dog", 3, id="empty-str-vs-bytes"),
        pytest.param(b"", "dog", 3, id="empty-bytes-vs-str"),
        pytest.param("kitten", b"sitting", 3, id="str-bytes-kitten-sitting"),
        pytest.param(b"kitten", "sitting", 3, id="bytes-str-kitten-sitting"),
        pytest.param("for", b"force", 2, id="str-bytes-prefix"),
    ],
)
@pytest.mark.parametrize(
    "fn",
    [
        pytest.param(classic, id="classic"),
        pytest.param(wagner_fischer, id="wagner_fischer"),
        pytest.param(wagner_fischer_native, id="native"),
        pytest.param(levenshtein, id="levenshtein"),
    ],
)
def test_distance(
    a: str | bytes,
    b: str | bytes,
    distance: int,
    fn: LevenshteinFn,
) -> None:
    assert fn(a, b) == distance
