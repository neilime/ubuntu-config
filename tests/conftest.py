"""TestInfra configuration and fixtures for ubuntu-config tests."""

import shlex

import pytest
import testinfra

DESKTOP_ENTRY_SEARCH_PATHS = (
    "/usr/share/applications",
    "/usr/local/share/applications",
    "/var/lib/flatpak/exports/share/applications",
)


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


def _build_desktop_entry_find_cmd(
    desktop_entry_pattern: str,
    search_paths: tuple[str, ...] = DESKTOP_ENTRY_SEARCH_PATHS,
) -> str:
    quoted_paths = " ".join(shlex.quote(path) for path in search_paths)
    quoted_pattern = shlex.quote(desktop_entry_pattern)
    return f"find {quoted_paths} -name {quoted_pattern} 2>/dev/null || true"


@pytest.fixture(scope="session")
def find_desktop_entries():
    """Return a callable that finds desktop entries on the target host."""

    def _find(test_host, desktop_entry_pattern: str) -> str:
        cmd = test_host.run(_build_desktop_entry_find_cmd(desktop_entry_pattern))
        return cmd.stdout.strip()

    return _find


def check_desktop_entries_exist(test_host, desktop_entries):
    """
    Check if desktop entries exist in common desktop entry locations.

    Args:
        test_host: testinfra host object
        desktop_entries: list of desktop entry filenames to check
    """

    for entry in desktop_entries:
        desktop_cmd = test_host.run(_build_desktop_entry_find_cmd(entry))
        assert desktop_cmd.stdout.strip(), f"Desktop entry for {entry} should exist"
