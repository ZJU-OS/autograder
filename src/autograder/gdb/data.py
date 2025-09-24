"""
GDB/MI Data Manipulation
"""

from .utils import write


def data_disassemble(test, start_addr: str, end_addr: str = "", mode: str = "0") -> list[dict]:
    """
    The corresponding GDB command is ‘disassemble’.
    """
    if end_addr:
        return write(f"-data-disassemble -s {start_addr} -e {end_addr} -- {mode}")
    else:
        return write(test, f"-data-disassemble -s {start_addr} -- {mode}")


def data_evaluate_expression(test, expr: str) -> list[dict]:
    """
    The corresponding GDB command is ‘print’, ‘output’, and ‘call’.
    """
    return write(test, f"-data-evaluate-expression {expr}")


def data_list_changed_registers(test) -> list[dict]:
    return write(test, "-data-list-changed-registers")


def data_list_register_names(test) -> list[dict]:
    return write(test, "-data-list-register-names")


def data_list_register_values(test, fmt: str = "x", regno: int = -1) -> list[dict]:
    """
    The corresponding GDB command is ‘info reg’.
    """
    if regno >= 0:
        return write(test, f"-data-list-register-values {fmt} {regno}")
    else:
        return write(test, f"-data-list-register-values {fmt}")


def data_read_memory(
    test,
    address: int,
    word_format: str = "i8",
    word_size: int = 1,
    nr_rows: int = 1,
    nr_cols: int = 16,
    ignore_error: bool = True,
) -> list[dict]:
    """
    The corresponding GDB command is ‘x’.
    """
    return write(
        f"-data-read-memory 0x{address:x} {word_format} {word_size} {nr_rows} {nr_cols}",
        raise_error_on_timeout=not ignore_error,
    )


def data_read_memory_bytes(
    test,
    address: str,
    count: int,
    offset: int = 0,
    ignore_error: bool = True,
) -> list[dict]:
    """
    The corresponding GDB command is ‘x’.
    """
    if offset > 0:
        return write(
            test,
            f"-data-read-memory-bytes {address} {count} {offset}",
            raise_error_on_timeout=not ignore_error,
        )
    else:
        return write(
            test,
            f"-data-read-memory-bytes {address} {count}",
            raise_error_on_timeout=not ignore_error,
        )
