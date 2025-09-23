import importlib

from autograder.core.options import parse_args_and_update_config
from autograder.core.testing import run_tests, _test_manager


def run_lab_tests(lab_num, test_filters):
    if lab_num is None:
        print("Could not determine lab number.")
        return

    total_score = 0
    total_possible = 0

    for i in range(1, lab_num + 1):
        try:
            print(f"Running tests for lab{i}")
            _test_manager.reset()
            importlib.import_module(f"tests.lab{i}")
            run_tests(test_filters)
            total_score += _test_manager.total
            total_possible += _test_manager.possible
        except ImportError:
            print(f"Could not find tests for lab{i}")
        except Exception as e:
            print(f"An error occurred while running tests for lab{i}: {e}")

    print(f"Total Score: {total_score}/{total_possible}")


if __name__ == "__main__":
    lab_num, test_filters = parse_args_and_update_config()
    run_lab_tests(lab_num, test_filters)
