# This implementation is based on QemuBaseTest from the QEMU project.
# Original code by https://gitlab.com/qemu-project/qemu, adapted for ZJU-OS testing.
import logging
import os
import unittest
import uuid
from pathlib import Path

from pygdbmi.gdbcontroller import GdbController
from qemu.machine import QEMUMachine

from . import gdb
from .config import config
from .qemu import console, monitor


class QemuGdbTest(unittest.TestCase):
    def log_file(self, *args):
        return str(Path(self.outputdir, *args))

    # def socket_dir(self):
    #     if self.socketdir is None:
    #         self.socketdir = tempfile.TemporaryDirectory(prefix="qemu_func_test_sock_")
    #     return self.socketdir

    def setUp(self):
        self.qemu_bin = config.qemu_bin
        self.assertIsNotNone(self.qemu_bin, "qemu_bin must be set")
        self.arch = self.qemu_bin.split("-")[-1]
        # self.socketdir = None # 用于给虚拟机输入
        self.outputdir = config.outputdir
        self.workdir = os.path.join(self.outputdir, "scratch")
        os.makedirs(self.workdir, exist_ok=True)

        self.log_filename = self.log_file("autograder.log")
        self.log = logging.getLogger("autograder")
        self.log.setLevel(logging.DEBUG)
        self._log_fh = logging.FileHandler(self.log_filename, mode="w")
        self._log_fh.setLevel(logging.DEBUG)
        self.fileFormatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        self._log_fh.setFormatter(self.fileFormatter)
        self.log.addHandler(self._log_fh)

        try:
            self.launch_vm()
            self.launch_gdb()
            self.run_to_kernel()
        except Exception as e:
            self.tearDown()
            raise e

    def launch_vm(self):
        # QEMU Machine 日志
        self.machinelog = logging.getLogger("qemu.machine")
        self.machinelog.setLevel(logging.DEBUG)
        self.machinelog.addHandler(self._log_fh)
        self.qmplog = logging.getLogger("qemu.qmp")
        self.qmplog.setLevel(logging.DEBUG)
        self.qmplog.addHandler(self._log_fh)

        # VM 控制台日志
        self.console_log_name = self.log_file("console.log")
        try:
            os.remove(self.console_log_name)
        except FileNotFoundError:
            pass

        name = str(uuid.uuid4())

        self.vm = QEMUMachine(
            self.qemu_bin,
            name=name,
            base_temp_dir=self.workdir,
            console_log=self.console_log_name,
        )
        self.vm.add_args(*config.qemu_args)
        self.vm.set_machine("virt")
        self.vm.set_console()
        self.vm.set_qmp_monitor()
        # 调试用 QMP monitor backdoor socket
        # 可使用 qmp-shell 连接
        # https://www.qemu.org/docs/master/devel/testing/functional.html#debugging-hung-qemu
        # sockfile = os.path.join(self.workdir, f"qemu-backdoor-{name}.sock")
        # self.vm.add_args(
        #     "-chardev",
        #     f"socket,id=backdoor,path={sockpath},server=on,wait=off",
        #     "-mon",
        #     "chardev=backdoor,mode=control",
        # )
        self.vm.launch()
        monitor.query_version(self)

    def launch_gdb(self):
        # GDB 日志
        self.gdb_log_name = self.log_file("gdb.log")
        self.gdb_log = logging.getLogger("gdb")
        self.gdb_log.setLevel(logging.DEBUG)
        self._gdb_log_fh = logging.FileHandler(self.gdb_log_name, mode="w")
        self._gdb_log_fh.setLevel(logging.DEBUG)
        self._gdb_log_fh.setFormatter(self.fileFormatter)
        self.gdb_log.addHandler(self._gdb_log_fh)

        # 创建 GDB
        cmd = ["gdb-multiarch", "--nx", "--quiet", "--interpreter=mi3"]
        self.gdb = GdbController(command=cmd)
        self.log.debug("GDB created with command: %s", " ".join(cmd))

        if not gdb.check_responses(
            gdb.target_select(self, "remote", f"localhost:{config.qemu_gdbstub_port}"), message="connected"
        ):
            raise Exception("Failed to connect to GDB stub on QEMU")

        if not gdb.check_responses(gdb.file_exec_and_symbols(self, config.vmlinux_path), message="done"):
            raise Exception("Failed to load executable and symbols")

    def run_to_kernel(self):
        gdb.check_responses(
            gdb.break_insert(self, gdb.locspec_address(0x80200000), temporary=True),
            message="done",
        )
        stopped = gdb.check_responses(gdb.exec_continue(self), message="stopped")
        console.wait_for_console_pattern(self, r"OpenSBI v")
        if not stopped:
            gdb.sync(self)

    def tearDown(self):
        # 清理 GDB
        self.gdb.exit()
        self.gdb_log.removeHandler(self._gdb_log_fh)
        self._gdb_log_fh.close()

        # 清理 VM

        self.vm.shutdown()
        # logging.getLogger("console").removeHandler(self._console_log_fh)
        # self._console_log_fh.close()

        # 清理自己

        # if self.socketdir is not None:
        #     shutil.rmtree(self.socketdir.name)
        #     self.socketdir = None
        self.machinelog.removeHandler(self._log_fh)
        self.log.removeHandler(self._log_fh)
        self._log_fh.close()
