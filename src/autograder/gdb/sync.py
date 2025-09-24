import time

from ..config import config
from .exec import exec_continue
from .utils import check_responses


def sync(test, timeout: float = config.wait_timeout) -> None:
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
                    return
        else:
            test.gdb_log.debug("GDB sync: no response, still waiting...")
            time.sleep(config.frequency)
    raise TimeoutError("Timeout waiting for GDB to stop")


def cont_sync(test, timeout: float = config.wait_timeout) -> None:
    if check_responses(exec_continue(test), message="stopped"):
        return
    sync(test, timeout=timeout)
