"""End-to-end checks for managed Flatpak applications."""


def test_flathub_remote_is_configured(host) -> None:
    """The installed machine should configure the declared Flatpak remote."""

    # Arrange
    remote_command = "flatpak remotes --system --columns=name"

    # Act
    remote_result = host.run(remote_command)

    # Assert
    assert remote_result.succeeded
    assert "flathub" in remote_result.stdout.splitlines()


def test_declared_flatpak_applications_are_installed(host) -> None:
    """The installed machine should install the declared Flatpak applications."""

    # Arrange
    application_command = "flatpak list --system --app --columns=application"

    # Act
    application_result = host.run(application_command)

    # Assert
    assert application_result.succeeded
    assert "com.bitwarden.desktop" in application_result.stdout.splitlines()
