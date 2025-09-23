import time

from pygdbmi.gdbcontroller import GdbController

from ..core.options import get_config

__all__ = ["GDB"]


class GDB:
    def __init__(
        self,
        run_args: list[str] = None,
    ):
        config = get_config()
        verbose = config.verbosity

        self.proc = None
        self.exec_path = get_config().test_dir + "/kernel/vmlinux"
        self.on_breakpoint: dict[int, tuple[callable, int]] = {}

        try:
            cmd = ["gdb-multiarch", "--nx", "--quiet", "--interpreter=mi3"]
            cmd += run_args if run_args else []
            if verbose:
                print(f"[VERBOSE] Starting GDB with command: {' '.join(cmd)}")
            self.proc = GdbController(command=cmd)

            # establish connection to QEMU's GDB stub
            self.gdbport = "1234"
            if verbose:
                print(f"[VERBOSE] Connecting to GDB stub on localhost:{self.gdbport}")
            response = self.proc.write(f"-target-select remote localhost:{self.gdbport}")

            # verify connection
            if not self.verify_connection(response):
                raise Exception("Failed to connect to GDB stub on QEMU")

            if verbose:
                print(f"[VERBOSE] Loading executable and symbols from {self.exec_path}")
            response = self.proc.write(f"-file-exec-and-symbols {self.exec_path}")

            if not self.is_done(response):
                raise Exception("Failed to load executable and symbols")

            if verbose:
                print("[VERBOSE] GDB initialized successfully")

        except Exception as e:
            raise e

    def verify_connection(self, response: list[dict]) -> bool:
        for r in response:
            if r["type"] == "result" and r["message"] == "connected":
                return True
        return False

    def is_done(self, response: list[dict]) -> bool:
        for r in response:
            if r["type"] == "result" and r["message"] == "done":
                return True
        return False

    def close(self):
        config = get_config()
        verbose = config.verbosity

        try:
            if self.proc:
                if verbose:
                    print("[VERBOSE] Closing GDB connection")
                # kill gdb
                self.proc.exit()
                if verbose:
                    print("[VERBOSE] GDB closed successfully")
        except Exception as e:
            print(f"""Error closing GDB connection: {e}.
You might need to execute 'killall gdb-multiarch' by yourself.""")

    def cont(self, ignore_error: bool = True) -> list[dict]:
        return self.proc.write("-exec-continue", raise_error_on_timeout=not ignore_error)

    def get_addr_from_response(self, response: list[dict]) -> int | None:
        for r in response:
            if r["message"] == "stopped" and r["payload"].get("reason", "") == "breakpoint-hit":
                if "frame" in r["payload"]:
                    frame = r["payload"]["frame"]
                    if "addr" in frame:
                        addr_str = frame["addr"]
                        try:
                            return int(addr_str, 16)
                        except ValueError:
                            pass
        return None

    def read_register(self, regname: str) -> int | None:
        response = self.proc.write(f"-data-evaluate-expression ${regname}")
        for r in response:
            if r["type"] == "result" and r["message"] == "done":
                if "value" in r["payload"]:
                    val_str = r["payload"]["value"]
                    try:
                        val = int(val_str, 0)
                        if val < 0:
                            val += 1 << 64  # convert to unsigned
                        return val
                    except ValueError:
                        pass
        return None

    def read_memory(self, addr: int, length: int) -> bytes | None:
        response = self.proc.write(f"-data-read-memory-bytes 0x{addr:x} {length}")
        for r in response:
            if r["type"] == "result" and r["message"] == "done":
                if "memory" in r["payload"]:
                    mem_list = r["payload"]["memory"]
                    if mem_list and "contents" in mem_list[0]:
                        hex_str = mem_list[0]["contents"]
                        try:
                            return bytes.fromhex(hex_str)
                        except ValueError:
                            pass
        return None

    def run(self, timeout: float = 30):
        from . import TerminateTest

        config = get_config()
        verbose = config.verbosity

        if verbose:
            print(f"[VERBOSE] GDB run starting with timeout {timeout}s, breakpoints: {list(self.on_breakpoint.keys())}")

        deadline = time.time() + timeout
        try:
            while self.on_breakpoint:
                timeleft = deadline - time.time()
                if timeleft < 0:
                    raise AssertionError("No termination after timeout!")

                if verbose:
                    print("[VERBOSE] Continuing execution in GDB")
                response = self.cont()

                if response == []:
                    raise Exception("No response from GDB after continuing.")

                hit_addr: int | None = self.get_addr_from_response(response)

                if not hit_addr:
                    # maybe still running
                    # wait for response
                    if verbose:
                        print("[VERBOSE] Waiting for GDB response")
                    response = self.proc.get_gdb_response(timeout_sec=timeleft, raise_error_on_timeout=False)
                    hit_addr = self.get_addr_from_response(response)
                    if not hit_addr:
                        raise AssertionError("GDB did not hit any breakpoint.")

                if hit_addr in self.on_breakpoint:
                    if verbose:
                        print(f"[VERBOSE] Hit breakpoint at address 0x{hit_addr:x}")
                    callback, times = self.on_breakpoint[hit_addr]
                    if callback:
                        callback(self)
                    if times > 0:
                        times -= 1
                        if times == 0:
                            del self.on_breakpoint[hit_addr]
                        else:
                            self.on_breakpoint[hit_addr] = (callback, times)

        except TerminateTest:
            if verbose:
                print("[VERBOSE] GDB run terminated by test")
            pass

        except Exception as e:
            if verbose:
                print(f"[VERBOSE] GDB run failed with exception: {e}")
            raise e

    def breakpoint(self, addr: int):
        self.proc.write(f"-break-insert *0x{addr:x}")
