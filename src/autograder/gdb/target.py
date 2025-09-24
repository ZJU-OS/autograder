"""
GDB/MI Target Manipulation Commands
"""

from .utils import write


def target_select(test, target_type: str, parameters: str) -> list[dict]:
    """
    The corresponding GDB command is ‘target’.
    Example: -target-select remote /dev/ttya
    """
    return write(test, f"-target-select {target_type} {parameters}")
