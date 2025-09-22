import json
import sys
import time
from typing import Callable, Dict, List, Optional

from .options import get_config, parse_args_and_update_config
from .utils import color
from .utils import make as utils_make
from .utils import reset_fs

__all__ = ["test", "end_part", "run_tests", "get_current_test"]


class TestManager:

    def __init__(self):
        self.tests: List[Callable] = []
        self.total = 0
        self.possible = 0
        self.part_total = 0
        self.part_possible = 0
        self.current_test: Optional[Callable] = None
        self.grades: Dict[str, int] = {}

    def reset(self):
        self.tests.clear()
        self.total = 0
        self.possible = 0
        self.part_total = 0
        self.part_possible = 0
        self.current_test = None
        self.grades.clear()


# Global test manager instance
_test_manager = TestManager()


def test(points: int,
         title: Optional[str] = None,
         parent: Optional[Callable] = None):

    def register_test(fn, title=title):
        if not title:
            assert fn.__name__.startswith("test_")
            title = fn.__name__[5:].replace("_", " ")
        if parent:
            title = "  " + title

        def run_test():
            # Handle test dependencies
            if run_test.complete:
                return run_test.ok
            run_test.complete = True
            parent_failed = False
            if parent:
                parent_failed = not parent()

            # Run the test
            fail = None
            start = time.time()
            _test_manager.current_test = run_test
            sys.stdout.write("== Test %s == " % title)
            if parent:
                sys.stdout.write("\n")
            sys.stdout.flush()

            try:
                if parent_failed:
                    raise AssertionError("Parent failed: %s" % parent.__name__)
                fn()
            except AssertionError as e:
                fail = str(e)

            # Display and handle test result
            _test_manager.possible += points
            if points:
                status = color("red", "FAIL") if fail else color("green", "OK")
                print("%s: %s" % (title, status), end=" ")

            if time.time() - start > 0.1:
                print("(%.1fs)" % (time.time() - start), end=" ")
            print()

            if fail:
                print("    %s" % fail.replace("\n", "\n    "))
            else:
                _test_manager.total += points

            if points:
                _test_manager.grades[title] = 0 if fail else points

            for callback in run_test.on_finish:
                callback(fail)
            _test_manager.current_test = None

            run_test.ok = not fail
            return run_test.ok

        # Record test metadata on the test wrapper function
        run_test.__name__ = fn.__name__
        run_test.title = title
        run_test.complete = False
        run_test.ok = False
        run_test.on_finish = []
        _test_manager.tests.append(run_test)
        return run_test

    return register_test


def end_part(name: str):

    def show_part():
        print("Part %s score: %d/%d" % (
            name,
            _test_manager.total - _test_manager.part_total,
            _test_manager.possible - _test_manager.part_possible,
        ))
        print()
        _test_manager.part_total = _test_manager.total
        _test_manager.part_possible = _test_manager.possible

    show_part.title = ""
    _test_manager.tests.append(show_part)


def write_results():
    config = get_config()
    if not config.result_path:
        return
    try:
        with open(config.result_path, "w") as f:
            f.write(json.dumps(_test_manager.grades))
    except OSError as e:
        print("Provided a bad results path. Error:", e)


def run_tests():
    # Parse command line arguments and update global config
    test_filters = parse_args_and_update_config()

    # Start with a full build to catch build errors
    utils_make()

    # Clean the file system if there is one
    reset_fs()

    # Run tests
    limit = list(map(str.lower, test_filters))
    try:
        for test_func in _test_manager.tests:
            if not limit or any(lim in test_func.title.lower()
                                for lim in limit):
                test_func()
        if not limit:
            write_results()
            print("Score: %d/%d" %
                  (_test_manager.total, _test_manager.possible))
    except KeyboardInterrupt:
        pass

    if _test_manager.total < _test_manager.possible:
        sys.exit(1)


def get_current_test():
    if not _test_manager.current_test:
        raise RuntimeError("No test is running")
    return _test_manager.current_test
