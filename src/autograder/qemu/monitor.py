"""
https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html
"""

from qemu.machine import QEMUMachine
from qemu.qmp.message import Message as QMPMessage

from ..testcase import QemuGdbTest

_supported_qmp_commands = None

def execute(test: QemuGdbTest, command: str, arguments: dict = None) -> QMPMessage:
    vm: QEMUMachine = test.vm
    global _supported_qmp_commands
    if _supported_qmp_commands is None:
        _supported_qmp_commands = set()
        response = vm.qmp("query-commands")
        if response and "return" in response:
            for cmd in response["return"]:
                name = cmd.get("name")
                if name:
                    _supported_qmp_commands.add(name)
    if command not in _supported_qmp_commands:
        raise RuntimeError(f"QMP command '{command}' not supported by this QEMU")
    return vm.qmp(command, arguments or {})

def query_version(test: QemuGdbTest) -> QMPMessage:
    return execute(test, "query-version")

def memsave(test: QemuGdbTest, val: int, size: int, filename: str, cpu_index: int = 0):
    args = {
        "val": val,
        "size": size,
        "filename": filename,
        "cpu-index": cpu_index
    }
    # Remove cpu-index if default (QEMU uses 0 by default)
    if cpu_index == 0:
        args.pop("cpu-index")
    execute(test, "memsave", args)

def pmemsave(test: QemuGdbTest, val: int, size: int, filename: str):
    args = {
        "val": val,
        "size": size,
        "filename": filename
    }
    execute(test, "pmemsave", args)

