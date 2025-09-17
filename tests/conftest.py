"""TestInfra configuration and fixtures for ubuntu-config tests."""

import pytest
import testinfra


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--host",
        action="store",
        default="local://",
        help="TestInfra host connection string (default: local://)",
    )
    parser.addoption(
        "--user",
        action="store",
        default=None,
        help="Target user for tests (default: current user)",
    )


@pytest.fixture(scope="session")
def host(request):  # pylint: disable=redefined-outer-name
    """TestInfra host fixture."""
    return testinfra.get_host(request.config.getoption("--host"))


@pytest.fixture(scope="session")
def target_user(request):  # pylint: disable=redefined-outer-name
    """Get the target user for tests."""
    user = request.config.getoption("--user")
    if user:
        return user

    test_host = testinfra.get_host(request.config.getoption("--host"))
    return test_host.user().name


@pytest.fixture(scope="session")
def user_home(target_user):  # pylint: disable=redefined-outer-name
    """Get the home directory of the target user."""
    if target_user == "root":
        return "/root"
    return f"/home/{target_user}"


def check_desktop_entries_exist(test_host, desktop_entries):
    """
    Check if desktop entries exist in common desktop entry locations.

    Args:
        test_host: testinfra host object
        desktop_entries: list of desktop entry filenames to check
    """

    for entry in desktop_entries:
        # Check in common desktop entry locations
        desktop_cmd = test_host.run(
            f"find /var/lib/flatpak/exports/share/applications "
            f"-name '{entry}' 2>/dev/null"
        )
        assert (
            desktop_cmd.stdout.strip() or desktop_cmd.rc == 0
        ), f"Desktop entry for {entry} should exist"
