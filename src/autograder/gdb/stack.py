"""
GDB/MI Stack Manipulation Commands
"""

from .utils import write


def stack_list_frames(test, low_frame: int = 0, high_frame: int = 0) -> list[dict]:
    """
    The corresponding GDB commands are ‘backtrace’ and ‘where’.
    """
    if high_frame > low_frame:
        return write(test, f"-stack-list-frames {low_frame} {high_frame}")
    else:
        return write(test, "-stack-list-frames")
