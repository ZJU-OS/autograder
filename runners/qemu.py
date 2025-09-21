import os
import select
import signal
import socket
import subprocess
import sys
import time
from subprocess import Popen
from typing import Callable, List, Optional

__all__ = ["QEMU"]


class QEMU:

    def __init__(self, *make_args: str):
        # Check that QEMU is not currently running
        try:
            gdbport = 1234
            sock = socket.create_connection(("localhost", gdbport), timeout=1)
        except (socket.error, ConnectionRefusedError):
            pass
        else:
            sock.close()
            print(
                f"""\
GDB stub found on port {gdbport}. It seems QEMU is already running.
Please exit it if possible or use 'killall qemu'.""",
                file=sys.stderr,
            )
            sys.exit(1)

        cmd = ("make", "debug") + make_args
        self.proc = Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            preexec_fn=os.setsid,
        )

        # Accumulated output as a string
        self.output = ""
        # Accumulated output as a bytearray
        self.outbytes = bytearray()
        # Callbacks for output events
        self.on_output: List[Callable[[bytes], None]] = []

    def run(self, timeout: float = 30):
        from . import TerminateTest

        if not self.proc:
            return

        deadline = time.time() + timeout
        try:
            while True:
                timeleft = deadline - time.time()
                if timeleft < 0:
                    sys.stdout.write("Timeout! ")
                    sys.stdout.flush()
                    raise AssertionError("Test timed out")

                _, _, _ = select.select([self.fileno()], [], [], timeleft)
                self.handle_read()
        except TerminateTest:
            # print("TerminateTest caught, exiting react loop")
            pass

    def fileno(self) -> Optional[int]:
        if self.proc:
            return self.proc.stdout.fileno()
        return None

    def handle_read(self):
        if not self.proc:
            return

        buf = os.read(self.proc.stdout.fileno(), 4096)
        self.outbytes.extend(buf)
        self.output = self.outbytes.decode("utf-8", "replace")

        # print(buf.decode("utf-8", "replace"), end="")

        for callback in self.on_output:
            callback(buf)

        if buf == b"":
            self.wait()

    def write(self, buf):
        if not self.proc:
            return

        if isinstance(buf, str):
            buf = buf.encode("utf-8")
        self.proc.stdin.write(buf)
        self.proc.stdin.flush()

    def close(self):
        if self.proc:
            try:
                pgid = os.getpgid(self.proc.pid)
                os.killpg(pgid, signal.SIGTERM)
            except Exception as e:
                print(f"Error terminating QEMU: {e}")
                raise e

            self.proc.wait()
            self.proc = None
