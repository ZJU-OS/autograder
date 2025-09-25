"""
GDB/MI Breakpoint Commands
"""

from .utils import write


def break_after(test, number: int, count: int) -> list[dict]:
    """
    The corresponding GDB command is ‘ignore’.
    """
    return write(test, f"-break-after {number} {count}")


def break_commands(test, number: int, *commands: str) -> list[dict]:
    """
    The corresponding GDB command is ‘commands’.
    """
    cmd_str = " ".join(f'"{c}"' for c in commands)
    return write(test, f"-break-commands {number} {cmd_str}".strip())


def break_condition(test, number: int, expr: str = "", force: bool = False) -> list[dict]:
    """
    The corresponding GDB command is ‘condition’.
    """
    force_flag = "--force " if force else ""
    if expr:
        return write(test, f"-break-condition {force_flag}{number} {expr}")
    else:
        return write(test, f"-break-condition {force_flag}{number}")


def break_delete(test, *numbers: int) -> list[dict]:
    """
    The corresponding GDB command is ‘delete’.
    """
    nums = " ".join(str(n) for n in numbers)
    return write(test, f"-break-delete {nums}")


def break_disable(test, *numbers: int) -> list[dict]:
    """
    The corresponding GDB command is ‘disable’.
    """
    nums = " ".join(str(n) for n in numbers)
    return write(test, f"-break-disable {nums}")


def break_enable(test, *numbers: int) -> list[dict]:
    """
    The corresponding GDB command is ‘enable’.
    """
    nums = " ".join(str(n) for n in numbers)
    return write(test, f"-break-enable {nums}")


def break_info(test, number: int) -> list[dict]:
    """
    The corresponding GDB command is ‘info break breakpoint’.
    """
    return write(test, f"-break-info {number}")


def break_insert(
    test,
    locspec: str,
    temporary: bool = False,
    hardware: bool = False,
    pending: bool = False,
    disabled: bool = False,
    tracepoint: bool = False,
    qualified: bool = False,
    condition: str = "",
    force_condition: bool = False,
    ignore_count: int | None = None,
    thread_id: int | None = None,
    thread_group_id: str = "",
    ignore_error: bool = True,
) -> list[dict]:
    """
    The corresponding GDB commands are ‘break’, ‘tbreak’, ‘hbreak’, and ‘thbreak’.
    """
    args = []
    if temporary:
        args.append("-t")
    if hardware:
        args.append("-h")
    if pending:
        args.append("-f")
    if disabled:
        args.append("-d")
    if tracepoint:
        args.append("-a")
    if qualified:
        args.append("--qualified")
    if condition:
        args.extend(["-c", condition])
    if force_condition:
        args.append("--force-condition")
    if ignore_count is not None:
        args.extend(["-i", str(ignore_count)])
    if thread_id is not None:
        args.extend(["-p", str(thread_id)])
    if thread_group_id:
        args.extend(["-g", thread_group_id])
    if locspec:
        args.append(locspec)
    cmd = " ".join(str(a) for a in args)
    return write(test, f"-break-insert {cmd}".strip())


def break_list(test) -> list[dict]:
    """
    The corresponding GDB command is ‘info breakpoints’.
    """
    return write(test, "-break-list")
