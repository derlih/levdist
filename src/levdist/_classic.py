def classic(a: str, b: str) -> int:
    """Calculate edit distance using a slow (classic) algorithm.

    Args:
        a (str): First string
        b (str): Second string

    Returns:
        int: Edit distance

    """
    if not a:
        return len(b)
    if not b:
        return len(a)

    head_a = a[0]
    tail_a = a[1:]
    head_b = b[0]
    tail_b = b[1:]

    if head_a == head_b:
        return classic(tail_a, tail_b)

    return 1 + min(classic(tail_a, b), classic(a, tail_b), classic(tail_a, tail_b))
