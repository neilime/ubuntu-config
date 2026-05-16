"""End-to-end checks for managed APT packages."""


def test_vendor_apt_repository_is_configured(host) -> None:
    """The installed machine should persist the declared vendor APT repository."""

    # Arrange
    keyring_file = host.file("/usr/share/keyrings/githubcli-archive-keyring.gpg")
    source_file = host.file("/etc/apt/sources.list.d/github-cli.list")

    # Act
    has_repository_url = source_file.contains("https://cli.github.com/packages")
    has_signed_by = source_file.contains(
        "signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    )

    # Assert
    assert keyring_file.exists
    assert source_file.exists
    assert has_repository_url
    assert has_signed_by


def test_declared_apt_packages_are_available(host) -> None:
    """The installed machine should install representative APT packages."""

    # Arrange
    htop_command = "command -v htop"
    github_cli_command = "command -v gh"

    # Act
    htop_result = host.run(htop_command)
    github_cli_result = host.run(github_cli_command)

    # Assert
    assert htop_result.succeeded
    assert github_cli_result.succeeded
