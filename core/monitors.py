import os
import re
import shutil
from typing import Callable, Union

from ..core.testing import get_current_test
from ..runners import Runner, TerminateTest

__all__ = [
    "save",
    "stop_breakpoint",
    "call_on_line",
    "stop_on_line",
    "call_on_breakpoint",
]


def save(path: str) -> Callable:

    def setup_save(runner):
        f.seek(0)
        f.truncate()
        runner.qemu.on_output.append(f.write)
        get_current_test().on_finish.append(save_on_finish)

    def save_on_finish(fail):
        f.flush()
        save_path = path + "." + get_current_test().__name__[5:]
        if fail:
            shutil.copyfile(path, save_path)
            print(f"    QEMU output saved to {save_path}")
        elif os.path.exists(save_path):
            os.unlink(save_path)
            print(f"    (Old {save_path} failure log removed)")

    f = open(path, "wb")
    return setup_save


def stop_breakpoint(addr: Union[str, int]) -> Callable:

    def setup_breakpoint(runner: Runner):
        if isinstance(addr, str):
            # Look up symbol address
            addrs = []
            try:
                with open("kernel/kernel.sym") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2 and parts[1] == addr:
                            addrs.append(int(parts[0], 16))
            except FileNotFoundError:
                pass
            assert addrs, f"Symbol {addr} not found"
            runner.gdb.breakpoint(addrs[0])
        else:
            runner.gdb.breakpoint(addr)

    return setup_breakpoint


def call_on_line(regexp: str, callback: Callable[[str], None]) -> Callable:

    def setup_call_on_line(runner: Runner):
        buf = bytearray()

        def handle_output(output: bytes):
            buf.extend(output)
            while b"\n" in buf:
                line_bytes, buf[:] = buf.split(b"\n", 1)
                line = line_bytes.decode("utf-8", "replace")
                if re.match(regexp, line):
                    callback(line)

        runner.qemu.on_output.append(handle_output)

    return setup_call_on_line


def call_on_breakpoint(addr: Union[str, int],
                       callback: Callable[[str], None] = None,
                       times: int = 1) -> Callable:

    def setup_call_on_breakpoint(runner: Runner):
        breakpoint_addr = addr
        if isinstance(addr, str):
            # Look up symbol address
            addrs = []
            try:
                with open("kernel/System.map") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 3 and parts[2] == addr:
                            addrs.append(int(parts[0], 16))
            except FileNotFoundError:
                pass
            assert addrs, f"Symbol {addr} not found"
            breakpoint_addr = addrs[0]

        runner.gdb.breakpoint(breakpoint_addr)
        runner.gdb.on_breakpoint[breakpoint_addr] = (callback, times)

    return setup_call_on_breakpoint


def stop_on_line(regexp: str) -> Callable:

    def stop(line: str):
        raise TerminateTest

    return call_on_line(regexp, stop)
