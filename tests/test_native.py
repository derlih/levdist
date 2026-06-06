import gc
from typing import Any

import psutil
import pytest
from levdist._native import wagner_fischer_native

try:
    import tracemalloc

    TRACEMALLOC_AVAILABLE = True
    MAX_MEMORY_DIFF_TRACEMALLOC = 1 * 1024 * 1024

except ImportError:
    TRACEMALLOC_AVAILABLE = False


# RSS memory can be more variable
MAX_MEMORY_DIFF_RSS = 10 * 1024 * 1024


@pytest.mark.parametrize(
    "params",
    [
        pytest.param((), id="no-params"),
        pytest.param(("a",), id="not-enough-params"),
        pytest.param(("a", "b", "c"), id="too-many-params"),
        pytest.param((1, "b"), id="wrong-type"),
    ],
)
def test_native_wrong_arguments(params: Any) -> None:  # noqa: ANN401
    with pytest.raises(TypeError):
        wagner_fischer_native(*params)


@pytest.mark.skipif(not TRACEMALLOC_AVAILABLE, reason="tracemalloc not available")
def test_native_no_mem_leak_tracemalloc() -> None:
    wagner_fischer_native("a-dog", "cat-b")

    tracemalloc.start()
    tracemalloc.clear_traces()

    for i in range(100_000):
        wagner_fischer_native(f"{i}-dog", f"cat-{i}")

    _, peak_traced = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert peak_traced < MAX_MEMORY_DIFF_TRACEMALLOC


def test_native_no_mem_leak_rss() -> None:
    wagner_fischer_native("a-dog", "cat-b")

    process = psutil.Process()
    gc.collect()
    before_rss = process.memory_info().rss

    for i in range(100_000):
        wagner_fischer_native(f"{i}-dog", f"cat-{i}")

    gc.collect()
    after_rss = process.memory_info().rss

    assert after_rss - before_rss < MAX_MEMORY_DIFF_RSS
