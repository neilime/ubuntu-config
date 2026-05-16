"""End-to-end checks for the system tests."""


def test_system_locale_configuration(host) -> None:
    """The installed machine should persist the configured locale."""

    # Arrange
    locale_file = host.file("/etc/default/locale")

    # Act
    has_lang = locale_file.contains("LANG=en_US.UTF-8")
    has_lc_all = locale_file.contains("LC_ALL=en_US.UTF-8")

    # Assert
    assert locale_file.exists
    assert has_lang
    assert has_lc_all


def test_system_timezone_configuration(host) -> None:
    """The installed machine should persist the configured timezone."""

    # Arrange
    timezone_file = host.file("/etc/timezone")

    # Act
    has_timezone = timezone_file.contains("Europe/Paris")
    localtime_target = host.check_output("readlink -f /etc/localtime")

    # Assert
    assert timezone_file.exists
    assert has_timezone
    assert localtime_target == "/usr/share/zoneinfo/Europe/Paris"


def test_system_sysctl_configuration(host) -> None:
    """The installed machine should apply the configured sysctl value."""

    # Arrange
    sysctl_file = host.file("/etc/sysctl.d/99-ubuntu-config.conf")

    # Act
    has_watch_limit = sysctl_file.contains("fs.inotify.max_user_watches = 524288")
    configured_watch_limit = host.check_output("sysctl -n fs.inotify.max_user_watches")

    # Assert
    assert sysctl_file.exists
    assert has_watch_limit
    assert configured_watch_limit == "524288"


def test_system_state_file(host) -> None:
    """The installation should write the system state marker."""

    # Arrange
    system_state = host.file("/etc/ubuntu-config-v1/system.json")

    # Act
    is_managed = system_state.contains('"managed": true')

    # Assert
    assert system_state.exists
    assert is_managed
