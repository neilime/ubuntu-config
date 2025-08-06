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
