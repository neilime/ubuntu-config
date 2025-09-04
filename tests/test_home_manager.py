"""Test Home Manager setup for user layer configuration."""


def test_home_manager_config_directory_exists(host):
    """Test that Home Manager configuration directory exists."""
    # Get the current user's home directory
    user = host.user()
    home_dir = user.home

    config_dir = host.file(f"{home_dir}/.config/home-manager")
    assert config_dir.exists, "Home Manager config directory should exist"
    assert config_dir.is_directory, "Home Manager config should be a directory"


def test_home_manager_flake_exists(host):
    """Test that Home Manager flake configuration exists."""
    user = host.user()
    home_dir = user.home

    flake_file = host.file(f"{home_dir}/.config/home-manager/flake.nix")
    assert flake_file.exists, "Home Manager flake.nix should exist"
    assert flake_file.contains(
        "home-manager"
    ), "flake.nix should reference home-manager"


def test_home_manager_home_nix_exists(host):
    """Test that home.nix configuration exists."""
    user = host.user()
    home_dir = user.home

    home_file = host.file(f"{home_dir}/.config/home-manager/home.nix")
    assert home_file.exists, "home.nix should exist"
    assert home_file.contains("programs.zsh.enable"), "home.nix should configure zsh"


def test_nix_profile_in_shell_config(host):
    """Test that Nix profile is added to shell configuration."""
    user = host.user()
    home_dir = user.home

    profile_file = host.file(f"{home_dir}/.profile")
    if profile_file.exists:
        assert profile_file.contains(
            "nix-daemon.sh"
        ), ".profile should source nix-daemon.sh"


def test_project_template_created(host):
    """Test that project template is created for users."""
    user = host.user()
    home_dir = user.home

    template_dir = host.file(f"{home_dir}/Documents/project-template")
    if template_dir.exists:
        flake_template = host.file(f"{home_dir}/Documents/project-template/flake.nix")
        envrc_template = host.file(f"{home_dir}/Documents/project-template/.envrc")

        assert flake_template.exists, "Project template flake.nix should exist"
        assert envrc_template.exists, "Project template .envrc should exist"
        assert envrc_template.contains("use flake"), ".envrc should contain 'use flake'"


def test_home_manager_command_available(host):
    """Test that home-manager command is available."""
    user = host.user()
    cmd = host.run_test(
        f"sudo -u {user.name} bash -c "
        f"'. /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && "
        f"which home-manager'"
    )
    assert cmd.rc == 0, "home-manager command should be available"
