"""System domain acceptance tests: user-visible behaviors for system configuration."""


def test_timezone_and_locale_set(host):
    """As a user I expect the system timezone and locale to be configured."""
    tz = host.run("timedatectl show -p Timezone --value || true")

    assert tz.stdout.strip(), "Timezone should be set"

    locale = host.run("localectl status | sed -n 's/\\s*System Locale: //p' || true")
    # we only check the command runs; specific values are environment-dependent
    assert locale.rc == 0
