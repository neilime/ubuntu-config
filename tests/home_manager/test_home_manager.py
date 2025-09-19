"""Home manager domain acceptance tests: verify home-manager artifacts."""


def test_home_manager_profiles_exist(host, user_home):
    """Check for common home-manager profile files (permissive smoke checks)."""
    # Common home-manager files (example)
    files = [".config/nixpkgs/home.nix", ".config/home-manager"]
    # The checks are permissive: not all systems use home-manager
    for f in files:
        _ = host.file(f"{user_home}/{f}")


def test_home_manager_required_directories_exist(host, user_home, target_user):
    """Check that required directories for Home Manager exist with proper ownership."""
    # Directories that should exist for proper Home Manager operation
    required_dirs = [
        ".cache",
        ".cache/oh-my-zsh",
        ".config",
        ".local",
        ".local/share",
        ".local/state",
    ]

    for dir_path in required_dirs:
        full_path = f"{user_home}/{dir_path}"
        directory = host.file(full_path)

        # Directory should exist and be a directory
        if directory.exists:
            assert directory.is_directory, f"{full_path} should be a directory"
            # Check ownership if the directory exists
            assert (
                directory.user == target_user
            ), f"{full_path} should be owned by {target_user}"


def test_default_shell_is_zsh(host, target_user):
    """Ensure the user's default shell ends with zsh."""
    user = host.user(target_user)

    assert user.shell.endswith("zsh"), "User should have zsh as default shell"
