import sys
import time
from typing import Any, Callable, List

from ..core.utils import post_make, pre_make
from .gdb import GDB
from .qemu import QEMU

__all__ = ["Runner"]


class TerminateTest(Exception):
    """Exception raised to terminate a test."""

    pass


class Runner:

    def __init__(self, *default_monitors: Callable[["Runner"], None]):
        self.default_monitors = default_monitors
        self.qemu: QEMU = None
        self.gdb: GDB = None

    def run(self, *monitors: Callable[["Runner"], None], **kw):

        def run_kw(
            test_on: str = "qemu",
            run_target: str = "debug",
            make_args: list[str] = [],
            timeout: float = 30,
        ):
            return test_on, run_target, make_args, timeout

        test_on, run_target, make_args, timeout = run_kw(**kw)

        # Start QEMU
        pre_make()
        self.qemu = QEMU(run_target, *make_args)
        self.gdb = None

        try:
            # Wait for QEMU to start or make to fail
            self.qemu.on_output = [self.monitor_start]
            self.qemu.run(timeout=90)

            # QEMU and GDB are up
            self.qemu.on_output = []

            if self.gdb is None:
                print("Failure when GDB is connecting to QEMU; output:")
                print(self.qemu.output)
                sys.exit(1)

            post_make()

            # Start monitoring
            for m in self.default_monitors + monitors:
                m(self)

            if test_on == "gdb":
                self.gdb.run(timeout)
            elif test_on == "qemu":
                self.gdb.cont()
                self.qemu.run(timeout)
            else:
                raise ValueError(
                    f"Unknown test_on: {test_on}. Must be 'qemu' or 'gdb'.")

        finally:
            # shutdown qemu and gdb
            try:
                if self.gdb is None:
                    # gdb is down, no need to close
                    sys.exit(1)
                self.qemu.close()
                self.gdb.close()
                self.qemu.run(timeout=5)
            except:
                print("""\
Failed to shutdown QEMU.  You might need to 'killall qemu' or
'killall qemu.real'.""")
                raise

    def monitor_start(self, output: bytes):
        if b"\n" in output:
            time.sleep(0.1)  # wait a bit for gdb stub to be ready
            self.gdb = GDB()
        if not len(output):
            raise Exception("No output from QEMU, likely failed.")

        raise TerminateTest

    def match(self, *args, **kwargs):
        from ..core.assertions import assert_lines_match

        assert_lines_match(self.qemu.output, *args, **kwargs)
