import argparse
import importlib
import os
import re
import subprocess
import unittest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lab", help="lab to test")

    args = parser.parse_args()

    lab_num = None
    if args.lab:
        match = re.match(r"lab(\d+)", args.lab)
        if match:
            lab_num = int(match.group(1))

    if lab_num is None:
        ci_branch = os.environ.get("CI_COMMIT_BRANCH")
        if ci_branch:
            match = re.match(r"lab(\d+)", ci_branch)
            if match:
                lab_num = int(match.group(1))

    if lab_num is None:
        try:
            branch_name = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip().decode()
            match = re.match(r"lab(\d+)", branch_name)
            if match:
                lab_num = int(match.group(1))
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    suite = unittest.TestSuite()
    try:
        module = importlib.import_module(f".tests.lab{lab_num}", package="autograder")
        loader = unittest.TestLoader()
        suite.addTests(loader.loadTestsFromModule(module))
    except ImportError as e:
        print(f"Could not find tests for lab{lab_num}")
        print(e)
    except Exception as e:
        print(f"An error occurred while loading tests for lab{lab_num}: {e}")

    # runner = pycotap.TAPTestRunner(message_log=pycotap.LogMode.LogToError, test_output_log=pycotap.LogMode.LogToError)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
