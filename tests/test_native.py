from typing import Any

import pytest
from levdist.native import wagner_fischer_native


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
