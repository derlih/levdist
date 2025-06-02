import gc
from typing import Any

import psutil
import pytest
from levdist._native import wagner_fischer_native


@pytest.mark.parametrize(
    "params",
    [
        pytest.param((), id="no-params"),
        pytest.param(("a",), id="not-enough-params"),
        pytest.param(("a", "b", "c"), id="too-many-params"),
        pytest.param((1, "b"), id="wrong-type"),
        pytest.param((b"a", b"b"), id="byte-type"),
    ],
)
def test_native_wrong_arguments(params: Any) -> None:  # noqa: ANN401
    with pytest.raises(TypeError):
        wagner_fischer_native(*params)


def test_native_no_mem_leak() -> None:
    # Warm up
    wagner_fischer_native("a-dog", "cat-b")

    process = psutil.Process()
    gc.collect()

    before = process.memory_info().rss
    iterations = 10_000_000

    for i in range(iterations):
        wagner_fischer_native(f"{i}-dog", "cat-{i}")

    gc.collect()
    after = process.memory_info().rss

    assert after - before < iterations
