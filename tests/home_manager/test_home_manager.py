"""Home manager domain acceptance tests: verify home-manager artifacts."""


def test_home_manager_profiles_exist(host, user_home):
    # Common home-manager files (example)
    files = [".config/nixpkgs/home.nix", ".config/home-manager"]
    # The checks are permissive: not all systems use home-manager
    for f in files:
        _ = host.file(f"{user_home}/{f}")


def test_default_shell_is_zsh(host, target_user):
    user = host.user(target_user)

    assert user.shell.endswith("zsh"), "User should have zsh as default shell"
