import autograder.gdb as g
import autograder.qemu.console as c
import autograder.qemu.monitor as m
from autograder.testcase import QemuGdbTest


def task1(self):
    g.break_insert(self, g.locspec_function("printk"), temporary=True)
    g.cont_sync(self)
    g.stack_list_frames(self)


def task2(self):
    g.break_insert(self, g.locspec_function("printk"), temporary=True)
    g.cont_sync(self)
    c.wait_for_console_pattern(self, r"Hello, ZJU OS 2025!")


def task3(self):
    g.break_insert(self, g.locspec_function("trap_handler"))
    g.cont_sync(self)
    scause = g.info_register(self, "scause")
    self.log.info(f"scause = {scause}")


def task4(self):
    # check sstatus
    g.cont_sync(self)
    scause = g.info_register(self, "scause")
    self.log.info(f"scause = {scause}")
    # check handler output
    g.cont_sync(self)
    c.wait_for_console_pattern(self, r"timer interrupt")


class Lab1Test(QemuGdbTest):
    def test_lab1(self):
        task1(self)
        print("Test1 Passed")
        task2(self)
        print("Test2 Passed")
        task3(self)
        print("Test3 Passed")
        task4(self)
        print("Test4 Passed")
