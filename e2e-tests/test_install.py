"""End-to-end checks for the install bootstrap tests."""


def test_install_bootstrap_tools_are_available(host) -> None:
    """The installed machine should have the bootstrap tools available."""

    # Arrange
    ansible_pull_command = "command -v ansible-pull"
    git_command = "command -v git"

    # Act
    ansible_pull_result = host.run(ansible_pull_command)
    git_result = host.run(git_command)

    # Assert
    assert ansible_pull_result.succeeded
    assert git_result.succeeded
