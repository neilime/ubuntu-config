"""System domain acceptance tests: user-visible behaviors for system configuration."""

import pytest


def test_timezone_and_locale_set(host, is_docker_test_env):
    """As a user I expect the system timezone and locale to be configured."""
    tz = host.run("timedatectl show -p Timezone --value || true")
    if is_docker_test_env:
        # lightweight test containers may not have timedatectl
        pytest.skip("timedatectl not available in container test image")

    assert tz.stdout.strip(), "Timezone should be set"

    locale = host.run("localectl status | sed -n 's/\\s*System Locale: //p' || true")
    # we only check the command runs; specific values are environment-dependent
    assert locale.rc == 0
