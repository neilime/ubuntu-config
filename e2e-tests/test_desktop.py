"""End-to-end checks for the desktop tests."""

import pytest


def test_desktop_dark_mode_preference(host) -> None:
    """The installed machine should persist the configured GNOME color scheme."""

    # Arrange
    color_scheme_command = (
        "dbus-run-session -- gsettings get org.gnome.desktop.interface color-scheme"
    )

    # Act
    color_scheme = host.check_output(color_scheme_command)

    # Assert
    assert color_scheme == "'prefer-dark'"


def test_desktop_favorites_preference(host) -> None:
    """The installed machine should persist the configured GNOME favorites."""

    # Arrange
    schema_check = host.run(
        "dbus-run-session -- gsettings list-schemas | grep -Fx org.gnome.shell"
    )
    favorites_command = (
        "dbus-run-session -- gsettings get org.gnome.shell favorite-apps"
    )

    if schema_check.rc != 0:
        pytest.skip("org.gnome.shell schema is not available in this environment")

    # Act
    favorites = host.check_output(favorites_command)

    # Assert
    assert favorites == "@as []"
