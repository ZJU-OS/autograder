import errno
import os
import random
import re
import shutil
import string
import sys
import time
from subprocess import Popen
from typing import List, Optional

from .options import get_config

__all__ = [
    "make",
    "maybe_unlink",
    "reset_fs",
    "color",
    "random_str",
    "check_time",
    "check_answers",
    "show_command",
    "pre_make",
    "post_make",
]

# Global state for make timing
MAKE_TIMESTAMP = 0

# Color definitions
COLORS = {"default": "\033[0m", "red": "\033[31m", "green": "\033[32m"}


def pre_make():
    """Delay prior to running make to ensure file mtimes change."""
    global MAKE_TIMESTAMP
    while int(time.time()) == MAKE_TIMESTAMP:
        time.sleep(0.1)


def post_make():
    """Record the time after make completes so that the next run of
    make can be delayed if needed."""
    global MAKE_TIMESTAMP
    MAKE_TIMESTAMP = int(time.time())


def make(*target: str):
    pre_make()
    config = get_config()
    cwd = config.test_dir if config.test_dir else os.getcwd()
    if Popen(("make", ) + target, cwd=cwd).wait():
        sys.exit(1)
    post_make()


def show_command(cmd: List[str]):
    from shlex import quote

    print("\n$", " ".join(map(quote, cmd)))


def maybe_unlink(*paths: str):
    for path in paths:
        try:
            os.unlink(path)
        except EnvironmentError as e:
            if e.errno != errno.ENOENT:
                raise


def color(name: str, text: str) -> str:
    config = get_config()
    if (config.color == "always") or \
       (config.color == "auto" and os.isatty(1)):
        return COLORS[name] + text + COLORS["default"]
    return text


def reset_fs():
    pass


def random_str(n: int = 8) -> str:
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(n))


def check_time():
    try:
        print("")
        with open("time.txt") as f:
            d = f.read().strip()
            if not re.match(r"^\d+$", d):
                raise AssertionError(
                    "time.txt does not contain a single integer "
                    "(number of hours spent on the lab)")
    except IOError:
        raise AssertionError("Cannot read time.txt")


def check_answers(file: str, n: int = 10):
    try:
        print("")
        with open(file) as f:
            d = f.read().strip()
            if len(d) < n:
                raise AssertionError(
                    f"{file} does not seem to contain enough text")
    except IOError:
        raise AssertionError(f"Cannot read {file}")
