import sys
import time
from collections.abc import Callable

from ..core.options import get_config
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
            make_args: list[str] = None,
            timeout: float = 30,
        ):
            if make_args is None:
                make_args = []
            return test_on, run_target, make_args, timeout

        test_on, run_target, make_args, timeout = run_kw(**kw)

        config = get_config()
        verbose = config.verbosity

        # Start QEMU
        if verbose:
            print(f"[VERBOSE] Starting QEMU with target '{run_target}' and args {make_args}")
        pre_make()
        self.qemu = QEMU(run_target, *make_args)
        self.gdb = None

        try:
            # Wait for QEMU to start or make to fail
            self.qemu.on_output = [self.monitor_start]
            if verbose:
                print("[VERBOSE] Waiting for QEMU to start...")
            self.qemu.run(timeout=90)

            # QEMU and GDB are up
            self.qemu.on_output = []

            if self.gdb is None:
                print("Failure when GDB is connecting to QEMU; output:")
                print(self.qemu.output)
                sys.exit(1)

            post_make()
            if verbose:
                print("[VERBOSE] QEMU and GDB are ready")

            # Start monitoring
            for m in self.default_monitors + monitors:
                m(self)

            if test_on == "gdb":
                if verbose:
                    print(f"[VERBOSE] Running test in GDB mode with timeout {timeout}s")
                self.gdb.run(timeout)
            elif test_on == "qemu":
                if verbose:
                    print(f"[VERBOSE] Running test in QEMU mode with timeout {timeout}s")
                self.gdb.cont()
                self.qemu.run(timeout)
            else:
                raise ValueError(f"Unknown test_on: {test_on}. Must be 'qemu' or 'gdb'.")

        finally:
            # shutdown qemu and gdb
            if verbose:
                print("[VERBOSE] Shutting down QEMU and GDB")
            cleanup_errors = []

            # Close GDB first
            if self.gdb is not None:
                try:
                    if verbose:
                        print("[VERBOSE] Closing GDB connection")
                    self.gdb.close()
                except Exception as e:
                    cleanup_errors.append(f"GDB close error: {e}")
                    if verbose:
                        print(f"[VERBOSE] Failed to close GDB: {e}")

            # Then close QEMU
            if self.qemu is not None:
                try:
                    if verbose:
                        print("[VERBOSE] Closing QEMU process")
                    self.qemu.close()
                    # Wait a bit for QEMU to fully terminate
                    self.qemu.run(timeout=5)
                except Exception as e:
                    cleanup_errors.append(f"QEMU close error: {e}")
                    if verbose:
                        print(f"[VERBOSE] Failed to close QEMU: {e}")

            if cleanup_errors:
                print("Cleanup errors occurred:")
                for error in cleanup_errors:
                    print(f"  {error}")
                print("""\
Failed to shutdown QEMU.  You might need to 'killall qemu' or
'killall qemu.real'.""")
                # Do not raise here to avoid masking the original test failure

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
