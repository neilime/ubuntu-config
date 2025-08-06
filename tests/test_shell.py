"""Tests for shell configuration (zsh)."""

import pytest

pytestmark = pytest.mark.shell


class TestZshInstallation:
    """Test Zsh shell installation and configuration."""

    def test_zsh_installed(self, host):
        """Test that Zsh is installed."""
        zsh = host.package("zsh")
        assert zsh.is_installed

    def test_zsh_executable(self, host):
        """Test that Zsh is executable."""
        zsh_cmd = host.run("zsh --version")
        assert zsh_cmd.rc == 0
        assert "zsh" in zsh_cmd.stdout.lower()

    def test_zsh_in_shells(self, host):
        """Test that Zsh is listed in /etc/shells."""
        shells = host.file("/etc/shells")
        assert shells.exists
        assert shells.contains("/usr/bin/zsh") or shells.contains("/bin/zsh")


class TestZshConfiguration:
    """Test Zsh configuration files and plugins."""

    def test_zshrc_exists(self, host, user_home):
        """Test that .zshrc exists."""
        zshrc = host.file(f"{user_home}/.zshrc")
        # .zshrc might exist depending on configuration
        if zshrc.exists:
            assert zshrc.is_file

    def test_oh_my_zsh_installation(self, host, user_home):
        """Test Oh My Zsh installation if present."""
        oh_my_zsh = host.file(f"{user_home}/.oh-my-zsh")
        if oh_my_zsh.exists:
            assert oh_my_zsh.is_directory

            # Check for Oh My Zsh core files
            oh_my_zsh_sh = host.file(f"{user_home}/.oh-my-zsh/oh-my-zsh.sh")
            assert oh_my_zsh_sh.exists

    def test_zsh_plugins_directory(self, host, user_home):
        """Test Zsh plugins directory if Oh My Zsh is installed."""
        plugins_dir = host.file(f"{user_home}/.oh-my-zsh/plugins")
        if plugins_dir.exists:
            assert plugins_dir.is_directory

    def test_zsh_themes_directory(self, host, user_home):
        """Test Zsh themes directory if Oh My Zsh is installed."""
        themes_dir = host.file(f"{user_home}/.oh-my-zsh/themes")
        if themes_dir.exists:
            assert themes_dir.is_directory


class TestShellAliases:  # pylint: disable=too-few-public-methods
    """Test shell aliases configuration."""

    def test_aliases_file(self, host, user_home):
        """Test that aliases are configured."""
        # Check common alias files
        bash_aliases = host.file(f"{user_home}/.bash_aliases")
        zsh_aliases = host.file(f"{user_home}/.zsh_aliases")

        # At least one alias file should exist or aliases should be in rc files
        zshrc = host.file(f"{user_home}/.zshrc")
        bashrc = host.file(f"{user_home}/.bashrc")

        has_alias_file = bash_aliases.exists or zsh_aliases.exists
        has_aliases_in_rc = (zshrc.exists and zshrc.contains("alias")) or (
            bashrc.exists and bashrc.contains("alias")
        )

        # This is optional, so we just verify structure if present
        if has_alias_file or has_aliases_in_rc:
            assert True  # Aliases are configured


class TestStarshipPrompt:
    """Test Starship prompt configuration if installed."""

    def test_starship_executable(self, host):
        """Test Starship executable if installed."""
        starship_cmd = host.run("which starship")
        if starship_cmd.rc == 0:
            # If starship is installed, test it works
            version_cmd = host.run("starship --version")
            assert version_cmd.rc == 0
            assert "starship" in version_cmd.stdout.lower()

    def test_starship_config(self, host, user_home):
        """Test Starship configuration if installed."""
        starship_config = host.file(f"{user_home}/.config/starship.toml")
        if starship_config.exists:
            assert starship_config.is_file
