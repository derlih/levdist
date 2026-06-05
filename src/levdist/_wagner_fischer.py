def wagner_fischer(a: str | bytes, b: str | bytes) -> int:
    """Calculate edit distance using a fast (Wagner-Fisher) algorithm.

    Args:
        a (str | bytes): First string
        b (str | bytes): Second string

    Returns:
        int: Edit distance

    """
    seq_a = list(a) if isinstance(a, bytes) else [ord(c) for c in a]
    seq_b = list(b) if isinstance(b, bytes) else [ord(c) for c in b]

    len_a = len(seq_a)
    len_b = len(seq_b)
    v0 = list(range(len_b + 1))
    v1 = [0 for _ in range(len_b + 1)]

    for i in range(len_a):
        v1[0] = i + 1

        for j in range(len_b):
            deletion_cost = v0[j + 1] + 1
            insertion_cost = v1[j] + 1
            substitution_cost = v0[j] if seq_a[i] == seq_b[j] else v0[j] + 1

            v1[j + 1] = min(deletion_cost, insertion_cost, substitution_cost)

        v1, v0 = v0, v1

    return v0[len_b]
