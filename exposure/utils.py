"""
A collection of helpers
"""
import math
from typing import TypeVar

T = TypeVar("T", float, int)


def floor(number: T, signficant_digits: int) -> T:
    """
    >>> floor(1234, 2)
    1200
    >>> floor(0.1234, 3)
    0.123
    >>> floor(1.40010292921234, 2)
    1.4
    >>> floor(1234, 5)
    1234.0
    """
    digits_before_comma = math.floor(math.log10(number))
    number = number * 10 ** (signficant_digits - 1 - digits_before_comma)
    number = math.floor(number)
    number = number * 10 ** -(signficant_digits - 1 - digits_before_comma)
    return round(number, signficant_digits)
