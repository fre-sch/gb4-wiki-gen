from typing import Sequence


def is_sequence(value):
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
    )