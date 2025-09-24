"""
GDB/MI File Commands
"""

from .utils import write


def file_exec_and_symbols(test, file: str = "") -> list[dict]:
    """
    The corresponding GDB command is ‘file’.
    """
    if file:
        return write(test, f"-file-exec-and-symbols {file}")
    else:
        return write(test, "-file-exec-and-symbols")
