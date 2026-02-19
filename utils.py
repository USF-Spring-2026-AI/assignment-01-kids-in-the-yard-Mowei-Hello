"""
Utility Functions
CS 362/562 - Assignment 1
Shared helper functions used across multiple modules.
"""


def get_decade_string(year: int) -> str:
    """
    Convert a year to its decade string representation.

    Args:
        year: A year (e.g., 1957, 2023)

    Returns:
        The decade string (e.g., "1950s", "2020s")
    """
    decade_num = (year // 10) * 10
    return f"{decade_num}s"
