"""
GDB/MI Functions Packed as GDB command
"""

import time

from ..config import config
from .data import data_list_register_names, data_list_register_values
from .exec import exec_continue
from .utils import check_responses

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


def cont(test) -> list[dict]:
    return exec_continue(test)


def sync(test, timeout: float = config.wait_timeout) -> list[dict]:
    # loop and accumulate responses until we see a "stopped" event or timeout
    deadline = time.time() + timeout
    responses = []
    while time.time() < deadline:
        resp = test.gdb.get_gdb_response(timeout_sec=config.frequency, raise_error_on_timeout=False)
        if resp:
            responses.extend(resp)
            for r in resp:
                test.gdb_log.debug("GDB response: %s", r)
            for r in resp:
                if r["message"] == "stopped":
                    return responses
        else:
            test.gdb_log.debug("GDB sync: no response, still waiting...")
            time.sleep(config.frequency)
    raise TimeoutError("Timeout waiting for GDB to stop")


def cont_sync(test, timeout: float = config.wait_timeout) -> None:
    responses = exec_continue(test)
    if check_responses(responses, message="stopped"):
        return responses
    responses.extend(sync(test, timeout=timeout))
