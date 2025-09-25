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
    # check scause
    g.break_insert(self, g.locspec_function("trap_handler"), temporary=True)
    g.cont_sync(self)
    scause = g.info_register(self, "scause")
    assert scause == "0x8000000000000001"
    # back to start_kernel
    g.break_insert(self, g.locspec_function("clock"), temporary=True)
    g.cont_sync(self)


def task4(self):
    # check clock
    #g.break_insert(self, g.locspec_function("clock"), temporary=True)
    #time_end = int(g.data_evaluate_expression(self, "time_end")["paylod"]["value"])
    #time_start = int(g.data_evaluate_expression(self, "time_start")["paylod"]["value"])
    #assert time_end - time_start > 0
    # check sstatus
    g.break_insert(self, g.locspec_function("trap_handler"), temporary=True)
    g.cont_sync(self)
    scause = g.info_register(self, "scause")
    assert scause == "0x8000000000000005"
    # check handler output
    c.wait_for_console_pattern(self, r"timer interrupt")


class Lab1Test(QemuGdbTest):
    def test_lab1(self):
        task1(self)
        print("Task1 Passed")
        task2(self)
        print("Task2 Passed")
        task3(self)
        print("Task3 Passed")
        task4(self)
        print("Task4 Passed")
