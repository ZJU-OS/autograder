"""
GDB/MI Program Execution
"""

from .utils import write


def exec_continue(test) -> list[dict]:
    """
    The corresponding GDB command is ‘continue’.
    """
    return write(test, "-exec-continue")


def exec_finish(test) -> list[dict]:
    """
    The corresponding GDB command is ‘finish’.
    """
    return write(test, "-exec-finish")


def exec_jump(test, location: str) -> list[dict]:
    """
    The corresponding GDB command is ‘jump’.
    """
    return write(test, f"-exec-jump {location}")


def exec_next(test) -> list[dict]:
    """
    The corresponding GDB command is ‘next’.
    """
    return write(test, "-exec-next")


def exec_next_instruction(test) -> list[dict]:
    """
    The corresponding GDB command is ‘nexti’.
    """
    return write(test, "-exec-next-instruction")


def exec_return(test) -> list[dict]:
    """
    The corresponding GDB command is ‘return’.
    """
    return write(test, "-exec-return")


def exec_run(test, args: str = "") -> list[dict]:
    """
    The corresponding GDB command is ‘run’.
    """
    if args:
        return write(test, f"-exec-run {args}")
    else:
        return write(test, "-exec-run")


def exec_step(test) -> list[dict]:
    """
    The corresponding GDB command is ‘step’.
    """
    return write(test, "-exec-step")


def exec_step_instruction(test) -> list[dict]:
    """
    The corresponding GDB command is ‘stepi’.
    """
    return write(test, "-exec-step-instruction")


def exec_until(test, location: str) -> list[dict]:
    """
    The corresponding GDB command is ‘until’.
    """
    return write(test, f"-exec-until {location}")
