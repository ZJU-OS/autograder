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

options: Optional[object] = None

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


def make(*target: str, cwd: Optional[str] = None):
    """
    Run make with the specified targets.

    Args:
        *target: Make targets to build

    Raises:
        SystemExit: If make fails
    """
    pre_make()
    if Popen(("make", ) + target, cwd=cwd).wait():
        sys.exit(1)
    post_make()


def show_command(cmd: List[str]):
    """
    Display a command that will be executed.

    Args:
        cmd: Command and arguments as a list
    """
    from shlex import quote

    print("\n$", " ".join(map(quote, cmd)))


def maybe_unlink(*paths: str):
    """
    Remove files if they exist, ignoring ENOENT errors.

    Args:
        *paths: File paths to remove
    """
    for path in paths:
        try:
            os.unlink(path)
        except EnvironmentError as e:
            if e.errno != errno.ENOENT:
                raise


def color(name: str, text: str) -> str:
    """
    Apply color formatting to text.

    Args:
        name: Color name ('red', 'green', 'default')
        text: Text to colorize

    Returns:
        Colored text string
    """
    # global options
    # if (options and options.color == "always") or \
    #    (options and options.color == "auto" and os.isatty(1)):
    #     return COLORS[name] + text + COLORS["default"]
    # return text
    return COLORS[name] + text + COLORS["default"]


def reset_fs():
    """Reset the file system to a clean state if clean image exists."""
    if os.path.exists("obj/fs/clean-fs.img"):
        shutil.copyfile("obj/fs/clean-fs.img", "obj/fs/fs.img")


def random_str(n: int = 8) -> str:
    """
    Generate a random string of letters and digits.

    Args:
        n: Length of the random string

    Returns:
        Random string
    """
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(n))


def check_time():
    """
    Check that time.txt exists and contains a valid hour count.

    Raises:
        AssertionError: If time.txt is missing or invalid
    """
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
    """
    Check that an answers file contains sufficient content.

    Args:
        file: Path to the answers file
        n: Minimum number of characters required

    Raises:
        AssertionError: If file is missing or too short
    """
    try:
        print("")
        with open(file) as f:
            d = f.read().strip()
            if len(d) < n:
                raise AssertionError(
                    f"{file} does not seem to contain enough text")
    except IOError:
        raise AssertionError(f"Cannot read {file}")
