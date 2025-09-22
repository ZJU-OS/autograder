from autograder import (GDB, Runner, TerminateTest, assert_equal,
                        call_on_breakpoint, color, end_part, run_tests,
                        stop_on_line, test)

r = Runner()


@test(1)
def test_printk():
    r.run(call_on_breakpoint("printk", lambda gdb: print("")),
          test_on="gdb",
          timeout=5)


end_part("Lab 1 Task 1")


@test(1)
def test_hello_output():
    r.run(stop_on_line(r"Hello, ZJU OS 2025!"), test_on="qemu", timeout=5)


end_part("Lab 1 Task 2")


@test(1)
def test_software_scause():
    times = 5
    counter = 0

    def check_scause(gdb: GDB):
        nonlocal counter, times

        try:
            scause = gdb.read_register("scause")
            assert scause is not None
            expected = (1 << 63) | (1)
            assert_equal(scause, expected,
                         "scause should indicate software interrupt!")
            raise TerminateTest
        except AssertionError as e:
            if counter < times - 1:
                counter += 1
                pass
            else:
                raise e

    r.run(call_on_breakpoint("trap_handler", check_scause, times=times),
          test_on="gdb",
          timeout=15)


end_part("Lab 1 Task 3")


@test(1)
def test_timer_interrupt():
    times = 6
    counter = 0
    prev_mtime = None

    def check_timer_interrupt(gdb: GDB):
        nonlocal counter, prev_mtime, times

        try:
            scause = gdb.read_register("scause")
            assert scause is not None

            # Check if it's a timer interrupt
            expected = (1 << 63) | (5)
            assert_equal(scause, expected,
                         "scause should indicate timer interrupt!")

            # Read mtime value
            mtime_addr = 0x200bff8
            mtime = gdb.read_memory(mtime_addr, 8)
            current_mtime = int.from_bytes(mtime, byteorder='little')

            # From second interrupt onwards, compare with previous value
            if prev_mtime is not None:
                time_diff = current_mtime - prev_mtime
                time_interval = 5000000
                assert time_diff > 5000000, "`stimecmp` not set correctly, timer interrupt too frequent!"
                raise TerminateTest

            prev_mtime = current_mtime

        except AssertionError as e:
            if counter < times - 2:
                counter += 1
                pass
            else:
                raise e

    r.run(call_on_breakpoint("trap_handler",
                             check_timer_interrupt,
                             times=times),
          test_on="gdb",
          timeout=15)


end_part("Lab 1 Task 4")

if __name__ == "__main__":
    run_tests()
