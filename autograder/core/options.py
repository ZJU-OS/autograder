import argparse
import os
import re
import subprocess
from dataclasses import dataclass


@dataclass
class TestConfig:
    color: str = "auto"
    verbosity: bool = False
    test_dir: str = os.getcwd()
    result_path: str | None = None


# Global configuration instance
_global_config: TestConfig = TestConfig()


def get_config() -> TestConfig:
    return _global_config


def update_config(**kwargs):
    global _global_config
    for key, value in kwargs.items():
        if hasattr(_global_config, key):
            setattr(_global_config, key, value)


def parse_args_and_update_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="print commands")
    parser.add_argument(
        "--color",
        choices=["never", "always", "auto"],
        default="auto",
        help="never, always, or auto",
    )
    parser.add_argument("--results", help="results file path")
    parser.add_argument("--test-dir", default=".", help="directory to run tests in")
    parser.add_argument("--lab", help="lab to test")
    parser.add_argument("filters", nargs="*", help="test filters")

    args = parser.parse_args()

    update_config(
        verbosity=args.verbose,
        color=args.color,
        result_path=args.results,
        test_dir=args.test_dir,
    )

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

    return lab_num, args.filters
