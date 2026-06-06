def _to_ints(s: str | bytes) -> tuple[int, ...]:
    if isinstance(s, str):
        return tuple(ord(c) for c in s)
    return tuple(s)


def wagner_fischer(a: str | bytes, b: str | bytes) -> int:
    """Calculate edit distance using a fast (Wagner-Fisher) algorithm.

    Args:
        a (str | bytes): First string
        b (str | bytes): Second string

    Returns:
        int: Edit distance

    """
    len_a = len(a)
    len_b = len(b)

    if len_a == 0:
        return len_b
    if len_b == 0:
        return len_a
    if a == b:
        return 0

    if len_a < len_b:
        a, b = b, a
        len_a, len_b = len_b, len_a

    seq_a: tuple[int, ...] | str | bytes
    seq_b: tuple[int, ...] | str | bytes
    if isinstance(a, bytes) is not isinstance(b, bytes):
        seq_a = _to_ints(a)
        seq_b = _to_ints(b)
    else:
        seq_a = a
        seq_b = b

    v0 = list(range(len_b + 1))
    v1 = [0] * (len_b + 1)

    for i in range(len_a):
        v1[0] = i + 1

        for j in range(len_b):
            deletion_cost = v0[j + 1] + 1
            insertion_cost = v1[j] + 1
            substitution_cost = v0[j] if seq_a[i] == seq_b[j] else v0[j] + 1

            v1[j + 1] = min(deletion_cost, insertion_cost, substitution_cost)

        v1, v0 = v0, v1

    return v0[len_b]
