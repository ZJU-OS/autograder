import argparse
import os
import re
import subprocess
import importlib
from autograder.core.testing import run_tests, _test_manager


def get_lab_num():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab")
    args = parser.parse_args()
    if args.lab:
        match = re.match(r"lab(\d+)", args.lab)
        if match:
            return int(match.group(1))

    ci_branch = os.environ.get("CI_COMMIT_BRANCH")
    if ci_branch:
        match = re.match(r"lab(\d+)", ci_branch)
        if match:
            return int(match.group(1))

    try:
        branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()
        match = re.match(r"lab(\d+)", branch_name)
        if match:
            return int(match.group(1))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None


def run_lab_tests(lab_num):
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
            run_tests()
            total_score += _test_manager.total
            total_possible += _test_manager.possible
        except ImportError:
            print(f"Could not find tests for lab{i}")
        except Exception as e:
            print(f"An error occurred while running tests for lab{i}: {e}")

    print(f"Total Score: {total_score}/{total_possible}")


if __name__ == "__main__":
    lab_num = get_lab_num()
    run_lab_tests(lab_num)
