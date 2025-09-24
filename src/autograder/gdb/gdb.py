"""
GDB/MI Functions Packed as GDB command
"""

from .data import data_list_register_names, data_list_register_values

_register_name_to_number = None


def info_register(test, regname: str, fmt: str = "x") -> str:
    """
    Query GDB for the value of the register named regname in the given format.
    Uses data_list_register_names and data_list_register_values.
    Returns the register value as int, or None if not found.
    """
    global _register_name_to_number
    if _register_name_to_number is None:
        _register_name_to_number = {}
        response = data_list_register_names(test)
        for r in response:
            if r.get("type") == "result" and r.get("message") == "done":
                names = r.get("payload", {}).get("register-names", [])
                for idx, name in enumerate(names):
                    if name:
                        _register_name_to_number[name] = idx
    regno = _register_name_to_number.get(regname)
    if regno is None:
        return None
    response = data_list_register_values(test, fmt, regno)
    for r in response:
        if r.get("type") == "result" and r.get("message") == "done":
            values = r.get("payload", {}).get("register-values", [])
            for v in values:
                if int(v.get("number", -1)) == regno:
                    val_str = v.get("value")
                    try:
                        return val_str
                    except Exception:
                        return None
    return None
