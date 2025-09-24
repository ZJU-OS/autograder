# This implementation is based on test/functional/qemu_test/cmd.py from the QEMU project.
# Original code by https://gitlab.com/qemu-project/qemu, adapted for ZJU-OS testing.

import select
import time

from ..config import config


def _console_read_line_until_match(test, vm, success, failure):
    msg = bytes([])
    done = False
    while True:
        c = vm.console_socket.recv(1)
        if c is None:
            done = True
            test.fail(f"EOF in console, expected '{success}'")
            break
        msg += c

        if success in msg:
            done = True
            break
        if failure and failure in msg:
            done = True
            vm.console_socket.close()
            test.fail(f"'{failure}' found in console, expected '{success}'")

        if c == b"\n":
            break

    return done


def _console_interaction(test, success_message, failure_message, send_string, keep_sending=False, vm=None):
    assert not keep_sending or send_string
    assert success_message or send_string

    if vm is None:
        vm = test.vm

    timeout = config.wait_timeout

    test.log.debug(
        f"Console interaction: success_msg='{success_message}' "
        + f"failure_msg='{failure_message}' send_string='{send_string}' timeout={timeout}"
    )

    # We'll process console in bytes, to avoid having to
    # deal with unicode decode errors from receiving
    # partial utf8 byte sequences
    success_message_b = None
    if success_message is not None:
        success_message_b = success_message.encode()

    failure_message_b = None
    if failure_message is not None:
        failure_message_b = failure_message.encode()

    while True:
        if send_string:
            vm.console_socket.sendall(send_string.encode())
            if not keep_sending:
                send_string = None  # send only once

        # Only consume console output if waiting for something
        if success_message is None:
            if send_string is None:
                break
            continue

        if _console_read_line_until_match(test, vm, success_message_b, failure_message_b):
            break


def interrupt_interactive_console_until_pattern(test, success_message, failure_message=None, interrupt_string="\r"):
    assert success_message
    _console_interaction(test, success_message, failure_message, interrupt_string, True)


def wait_for_console_pattern(test, success_message, failure_message=None, vm=None):
    assert success_message
    _console_interaction(test, success_message, failure_message, None, vm=vm)


def exec_command(test, command):
    _console_interaction(test, None, None, command + "\r")


def exec_command_and_wait_for_pattern(test, command, success_message, failure_message=None):
    assert success_message
    _console_interaction(test, success_message, failure_message, command + "\r")
