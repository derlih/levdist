def _classic_impl(a: list[int], b: list[int]) -> int:
    if not a:
        return len(b)
    if not b:
        return len(a)
    if a[0] == b[0]:
        return _classic_impl(a[1:], b[1:])
    return 1 + min(
        _classic_impl(a[1:], b),
        _classic_impl(a, b[1:]),
        _classic_impl(a[1:], b[1:]),
    )


def classic(a: str | bytes, b: str | bytes) -> int:
    """Calculate edit distance using a slow (classic) algorithm.

    Args:
        a (str | bytes): First string
        b (str | bytes): Second string

    Returns:
        int: Edit distance

    """
    seq_a = list(a) if isinstance(a, bytes) else [ord(c) for c in a]
    seq_b = list(b) if isinstance(b, bytes) else [ord(c) for c in b]
    return _classic_impl(seq_a, seq_b)
