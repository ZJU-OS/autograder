"""
Global Helper Function
"""


def write(test, command: str) -> list[dict]:
    responses = test.gdb.write(command)
    test.gdb_log.debug("GDB command: %s", command)
    for r in responses:
        test.gdb_log.debug("GDB response: %s", r)
    return responses


def check_responses(
    response: list[dict],
    message: str = None,
    type: str = None,
) -> bool:
    for r in response:
        if (type is None or r.get("type") == type) and (message is None or r.get("message") == message):
            return True
    return False
