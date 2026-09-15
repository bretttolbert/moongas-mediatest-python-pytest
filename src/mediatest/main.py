import argparse
import hashlib
from importlib.metadata import version
import logging
import platform
import sys
from pathlib import Path

import pytest

from mediatest import config

logger = logging.getLogger(__name__)


def file_hash_sha256(file_path: Path):
    with open(file_path, "rb") as f:
        return hashlib.file_digest(f, "sha256")


def parse_log_level(value: str) -> int:
    level_name = value.upper()
    level = getattr(logging, level_name, None)
    if not isinstance(level, int):
        valid_levels = ", ".join(logging.getLevelNamesMapping())
        raise argparse.ArgumentTypeError(
            f"invalid log level: {value!r} (choose from {valid_levels})"
        )
    return level


def version_string() -> str:
    return (
        f"mediatest {version('mediatest')} "
        f"(mediascan {version('mediascan')}, "
        f"pytest {pytest.__version__}, "
        f"python {platform.python_version()})"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run mediatest media tests using the provided config YAML file",
    )
    parser.add_argument(
        "config_path",
        type=Path,
        help="Path to the mediatest config YAML file.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version_string(),
    )
    parser.add_argument(
        "--log-level",
        type=parse_log_level,
        default=logging.INFO,
        metavar="LEVEL",
        help="Logging level (default: INFO).",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="PATH",
        help="Path to ignore when collecting pytest tests; may be repeated.",
    )
    parser.add_argument(
        "-k",
        "--keyword",
        metavar="EXPRESSION",
        help="Only run tests matching the pytest expression.",
    )
    parser.add_argument(
        "-m",
        dest="marker_expression",
        metavar="MARKEXPR",
        help="Only run tests matching the pytest marker expression.",
    )
    parser.add_argument(
        "--lf",
        "--last-failed",
        dest="last_failed",
        action="store_true",
        help="Re-run only tests that failed during the previous execution.",
    )
    parser.add_argument(
        "--pdb",
        action="store_true",
        help="Drop into the Python debugger when a test fails.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase pytest output details.",
    )
    parser.add_argument(
        "-s",
        "--capture=no",
        dest="no_capture",
        action="store_true",
        help="Disable pytest output capture.",
    )
    parser.add_argument(
        "-x",
        "--exitfirst",
        action="store_true",
        help="Stop the test suite after the first failure.",
    )
    parser.add_argument(
        "--ff",
        "--failed-first",
        action="store_true",
        help="Run previously failed tests first, then the remaining tests.",
    )
    parser.add_argument(
        "--maxfail",
        type=int,
        metavar="NUM",
        help="Stop after NUM test failures or errors.",
    )
    parser.add_argument(
        "--durations",
        type=int,
        metavar="NUM",
        help="Report the NUM slowest test durations.",
    )
    parser.add_argument(
        "--durations-min",
        type=float,
        metavar="SECONDS",
        help="Only report test durations at least SECONDS long.",
    )
    args, additional_pytest_args = parser.parse_known_args()
    log_level = args.log_level
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.debug("main() starting")
    logger.debug("sys.argv before parsing: %s", sys.argv)
    logger.debug("argparse parsed args: %s", args)

    config_path = args.config_path
    logger.info("Received CLI config path: %s", config_path)
    logger.debug("config_path raw value: %r", config_path)
    logger.debug(
        "config_path absolute form before exists check: %s", config_path.absolute()
    )
    logger.debug(
        "config_path resolved form before exists check: %s", config_path.resolve()
    )

    logger.debug("Checking whether config file exists at %s", config_path)
    logger.debug("os.path.exists(%s) = %s", config_path, config_path.exists())
    logger.debug("is_file(%s) = %s", config_path, config_path.is_file())

    if not config_path.exists():
        logger.error("Config file missing: %s", config_path)
        parser.error(f"Config file does not exist: {config_path}")

    if not config_path.is_file():
        logger.error("Config path is not a file: %s", config_path)
        parser.error(f"Config path is not a file: {config_path}")

    hash = file_hash_sha256(config_path).hexdigest()
    logger.info(f'Loading config from "{config_path}" sha256:{hash} content:')

    with open(config_path, "r") as file:
        content = file.read()
        logger.info(
            "\n---BEGIN_MEDIATEST_CONFIGURATION---\n"
            + content
            + "\n---END_MEDIATEST_CONFIGURATION---\n"
        )

    logger.debug("Calling configure(%s)", config_path)
    config.configure(config_path)
    logger.info("configure(%s) completed successfully", config_path)

    if config.MEDIA_ROOTDIR:
        media_rootdir = Path(config.MEDIA_ROOTDIR)
        logger.debug("Resolved media_rootdir from config path: %s", media_rootdir)
    else:
        media_rootdir = config_path.resolve().parent
        logger.debug(
            "No config path provided for media_rootdir, defaulting to: %s",
            media_rootdir,
        )

    if config.MEDIATEST_ROOTDIR:
        mediatest_rootdir = Path(config.MEDIATEST_ROOTDIR)
        logger.debug(
            "Resolved mediatest_rootdir from config path: %s", mediatest_rootdir
        )
    else:
        mediatest_rootdir = config_path.resolve().parent
        logger.debug(
            "No config path provided for mediatest_rootdir, defaulting to: %s",
            mediatest_rootdir,
        )

    logger.debug("media_rootdir exists = %s", media_rootdir.exists())
    logger.debug("media_rootdir is_dir = %s", media_rootdir.is_dir())

    logger.debug("mediatest_rootdir exists = %s", mediatest_rootdir.exists())
    logger.debug("mediatest_rootdir is_dir = %s", mediatest_rootdir.is_dir())

    test_path = mediatest_rootdir / "tests" / "mediatests"
    logger.debug("Computed test_path=%s", test_path)
    logger.debug("test_path exists = %s", test_path.exists())
    logger.debug("test_path is_dir = %s", test_path.is_dir())

    log_level_name = next(
        name
        for name, value in logging.getLevelNamesMapping().items()
        if value == log_level
    )
    pytest_args = [
        str(test_path),
        "--rootdir",
        str(mediatest_rootdir),
        "-o",
        "log_cli=true",
        f"--log-cli-level={log_level_name}",
    ]
    for ignore_path in args.ignore:
        pytest_args.extend(["--ignore", ignore_path])
    if args.keyword is not None:
        pytest_args.extend(["-k", args.keyword])
    if args.marker_expression is not None:
        pytest_args.extend(["-m", args.marker_expression])
    if args.last_failed:
        pytest_args.append("--lf")
    if args.pdb:
        pytest_args.append("--pdb")
    if args.verbose:
        pytest_args.append("-v")
    if args.no_capture:
        pytest_args.append("-s")
    if args.exitfirst:
        pytest_args.append("-x")
    if args.ff:
        pytest_args.append("--ff")
    if args.maxfail is not None:
        pytest_args.append(f"--maxfail={args.maxfail}")
    if args.durations is not None:
        pytest_args.append(f"--durations={args.durations}")
    if args.durations_min is not None:
        pytest_args.append(f"--durations-min={args.durations_min}")
    pytest_args.extend(additional_pytest_args)
    logger.info("Executing pytest with args: %s", pytest_args)
    result = pytest.main(pytest_args)
    logger.info("pytest.main() returned %s", result)
    logger.debug("main() exiting with result=%s", result)

    sys.exit(int(result))
