from typing import Sequence
from slugify import slugify
from functools import partial
import re

def is_sequence(value):
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
    )


disallowed_chars = re.compile(r'[^-a-zA-Z0-9:]+')
slugify = partial(slugify,
                  lowercase=False,
                  separator="_",
                  regex_pattern=disallowed_chars)
