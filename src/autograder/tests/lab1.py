import autograder.gdb as g
import autograder.qemu.console as c
import autograder.qemu.monitor as m
from autograder.testcase import QemuGdbTest


def task1(self):
    responses = g.break_insert(self, g.locspec_function("printk"), temporary=True)
    bkpt_num = responses[0]["payload"]["bkpt"]["number"]
    responses = g.cont_sync(self)
    breakpoint_hit = False
    if responses is None:
        responses = g.sync(self)
    for r in responses:
        if r.get("type") == "notify" and r.get("message") == "stopped":
            payload = r.get("payload", {})
            if payload.get("reason") == "breakpoint-hit" and payload.get("bkptno") == bkpt_num:
                breakpoint_hit = True
    assert breakpoint_hit, "Breakpoint at printk was not hit"

    scause = g.info_register(self, "scause")
    assert scause == "0x0", f"Expected scause to be 0x0, got {scause}"


def task2(self):
    for _ in range(5):
        g.break_insert(self, g.locspec_function("printk"), temporary=True)
        g.cont_sync(self)
    c.wait_for_console_pattern(self, r"Hello, ZJU OS 2025!")


def task3(self):
    # check scause
    g.break_insert(self, g.locspec_function("_traps"), temporary=True)
    g.cont_sync(self)
    c.wait_for_console_pattern(self, r"sstatus:")
    c.wait_for_console_pattern(self, r"sie:")
    c.wait_for_console_pattern(self, r"sip:")
    scause = g.info_register(self, "scause")
    assert scause == "0x8000000000000001", f"Expected scause to be 0x8000000000000001, got {scause}"
    sip = g.info_register(self, "sip")
    sip_val = int(sip, 16)
    assert sip_val & 0x2 == 0x2, f"Expected SSIP to be 1, got {(sip_val & 0x2) >> 1}"
    sie = g.info_register(self, "sie")
    sie_val = int(sie, 16)
    assert sie_val & 0x2 == 0x2, f"Expected SSIE to be 1, got {(sie_val & 0x2) >> 1}"

    # back to start_kernel
    g.break_insert(self, g.locspec_function("clock"), temporary=True)
    responses = g.break_insert(self, g.locspec_function("_traps"), temporary=True)
    bkpt_num = responses[0]["payload"]["bkpt"]["number"]
    responses = g.cont_sync(self)
    another_trap = False
    if responses is None:
        responses = g.sync(self)
    for r in responses:
        if r.get("type") == "notify" and r.get("message") == "stopped":
            payload = r.get("payload", {})
            if payload.get("reason") == "breakpoint-hit" and payload.get("bkptno") == bkpt_num:
                another_trap = True
    assert not another_trap, "Another trap occurred before reaching clock"


def task4(self):
    # check clock
    responses = g.break_insert(self, g.locspec_function("clock"), temporary=True)
    bkpt_num = responses[0]["payload"]["bkpt"]["number"]
    responses = g.cont_sync(self)
    breakpoint_hit = False
    for r in responses:
        if r.get("type") == "notify" and r.get("message") == "stopped":
            payload = r.get("payload", {})
            if payload.get("reason") == "breakpoint-hit":
                if payload.get("bkptno") == bkpt_num:
                    breakpoint_hit = True
    assert breakpoint_hit, "Breakpoint at clock was not hit"

    g.exec_finish(self)
    time_end = int(g.data_evaluate_expression(self, "time_end")[0]["payload"]["value"])
    time_start = int(g.data_evaluate_expression(self, "time_start")[0]["payload"]["value"])
    assert time_end - time_start > 0, "Expected time_end to be greater than time_start"

    # check sstatus
    g.break_insert(self, g.locspec_function("_traps"), temporary=True)
    g.cont_sync(self)
    scause = g.info_register(self, "scause")
    assert scause == "0x8000000000000005"
    # check handler output
    g.cont(self)
    c.wait_for_console_pattern(self, r"timer interrupt")


class Lab1Test(QemuGdbTest):
    def test_lab1(self):
        print("")
        task1(self)
        print("Task1 Passed")
        task2(self)
        print("Task2 Passed")
        task3(self)
        print("Task3 Passed")
        task4(self)
        print("Task4 Passed")
