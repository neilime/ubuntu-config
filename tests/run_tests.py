"""Test runner script moved to legacy tests folder."""

import argparse
import os
import subprocess
import sys


def run_tests(
    host="local://", user=None, verbose=False, html_report=False, parallel=False
):
    """Run TestInfra tests."""
    cmd = ["python3", "-m", "pytest"]

    # Add test directory
    cmd.append(os.path.dirname(__file__))

    # Add TestInfra host connection
    cmd.extend(["--host", host])

    # Add user if specified
    if user:
        cmd.extend(["--user", user])

    # Add verbosity
    if verbose:
        cmd.append("-v")

    # Add HTML report
    if html_report:
        report_path = os.path.join(os.path.dirname(__file__), "test-report.html")
        cmd.extend(["--html", report_path, "--self-contained-html"])

    # Add parallel execution
    if parallel:
        cmd.extend(["-n", "auto"])

    # Run tests
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd, check=False).returncode


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run ubuntu-config TestInfra tests")
    parser.add_argument(
        "--host",
        default="local://",
        help="TestInfra host connection string (default: local://)",
    )
    parser.add_argument("--user", help="Target user for tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--html-report", action="store_true", help="Generate HTML test report"
    )
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")

    args = parser.parse_args()

    return run_tests(
        host=args.host,
        user=args.user,
        verbose=args.verbose,
        html_report=args.html_report,
        parallel=args.parallel,
    )


if __name__ == "__main__":
    sys.exit(main())
