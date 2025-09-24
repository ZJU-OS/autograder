"""
Location Specifications
"""


def locspec_line(line: int) -> str:
    """Location spec for a line number in the current source file."""
    return str(line)


def locspec_file_line(filename: str, line: int) -> str:
    """Location spec for a line number in a specific file."""
    return f"{filename}:{line}"


def locspec_function(function: str) -> str:
    """Location spec for a function name."""
    return function


def locspec_file_function(filename: str, function: str) -> str:
    """Location spec for a function in a specific file."""
    return f"{filename}:{function}"


def locspec_function_label(function: str, label: str) -> str:
    """Location spec for a label in a function."""
    return f"{function}:{label}"


def locspec_label(label: str) -> str:
    """Location spec for a label in the current function."""
    return label


def locspec_address(address: int | str) -> str:
    """Location spec for an address (as int or hex string)."""
    if isinstance(address, int):
        return f"*0x{address:x}"
    return f"*{address}"


def locspec_explicit(
    source: str = "",
    function: str = "",
    label: str = "",
    line: int | str = "",
    qualified: bool = False,
) -> str:
    """
    Build an explicit location spec using GDB's option-value pairs.
    """
    args = []
    if qualified:
        args.append("--qualified")
    if source:
        args.extend(["--source", source])
    if function:
        args.extend(["--function", function])
    if label:
        args.extend(["--label", label])
    if line != "" and line is not None:
        args.extend(["--line", str(line)])
    return " ".join(args)
