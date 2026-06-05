import gc
import tracemalloc
from typing import Any

import psutil
import pytest
from levdist._native import wagner_fischer_native

MAX_MEMORY = 1 * 1024 * 1024


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
    # warm up
    wagner_fischer_native("a-dog", "cat-b")

    process = psutil.Process()
    gc.collect()
    before_rss = process.memory_info().rss

    tracemalloc.start()
    tracemalloc.clear_traces()

    for i in range(100_000):
        wagner_fischer_native(f"{i}-dog", f"cat-{i}")

    _, peak_traced = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    gc.collect()
    after_rss = process.memory_info().rss

    assert peak_traced < MAX_MEMORY  # PyMem_* leaks (precise)
    assert after_rss - before_rss < MAX_MEMORY  # raw malloc leaks (broad)
