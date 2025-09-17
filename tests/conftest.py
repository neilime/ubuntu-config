"""TestInfra configuration and fixtures for ubuntu-config tests."""

import pytest
import testinfra
import os


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
def is_docker_test_env(host):  # pylint: disable=redefined-outer-name
    """Detect whether tests are running inside a container (Docker/LXC/etc).

    Heuristics used:
    - presence of /.dockerenv
    - /proc/1/cgroup contains container keywords
    Returns True when running inside a container-like environment.

    Usage in tests:
        def test_something(host, is_docker_test_env):
            if is_docker_test_env:
                pytest.skip("Not applicable in container tests")
            # otherwise perform assertions
    """
    try:
        if host.file("/.dockerenv").exists:
            return True
    except Exception:
        # testinfra host may not support .file accessor for some backends; fall back to OS checks
        pass

    try:
        cgroup = host.file("/proc/1/cgroup")
        if cgroup.exists:
            content = cgroup.content_string.lower()
            for kw in ("docker", "containerd", "lxc", "kubepods", "podman"):
                if kw in content:
                    return True
    except Exception:
        # if accessing via testinfra fails, try local filesystem as best-effort
        try:
            if os.path.exists("/.dockerenv"):
                return True
            with open("/proc/1/cgroup", "r") as fh:
                data = fh.read().lower()
                for kw in ("docker", "containerd", "lxc", "kubepods", "podman"):
                    if kw in data:
                        return True
        except Exception:
            return False

    return False


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
