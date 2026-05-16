"""End-to-end checks for the user tests."""


def test_user_state_file(host) -> None:
    """The installation should write the user state marker."""

    # Arrange
    user_name = host.check_output("whoami")
    user_home = host.check_output("printf '%s' \"$HOME\"")
    user_state = host.file(f"{user_home}/.local/state/ubuntu-config-v1/state.json")

    # Act
    is_managed = user_state.contains('"managed": true')
    has_user_name = user_state.contains(f'"user": "{user_name}"')

    # Assert
    assert user_state.exists
    assert is_managed
    assert has_user_name
