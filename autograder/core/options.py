import os
from dataclasses import dataclass
from optparse import OptionParser


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
    parser = OptionParser(usage="usage: %prog [-v] [--color=WHEN] [--results=FILE] [filters...]")
    parser.add_option("-v", "--verbose", action="store_true", help="print commands")
    parser.add_option(
        "--color",
        choices=["never", "always", "auto"],
        default="auto",
        help="never, always, or auto",
    )
    parser.add_option("--results", help="results file path")
    parser.add_option("--test-dir", default=".", help="directory to run tests in")

    (options, args) = parser.parse_args()

    update_config(
        verbosity=options.verbose,
        color=options.color,
        result_path=options.results,
        test_dir=options.test_dir,
    )

    return args
