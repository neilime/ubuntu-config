"""Tests for SSH and GPG keys setup."""

import pytest

pytestmark = pytest.mark.keys


class TestSshKeys:
    """Test SSH keys configuration."""

    def test_ssh_directory_exists(self, host, user_home):
        """Test that .ssh directory exists with proper permissions."""
        ssh_dir = host.file(f"{user_home}/.ssh")
        assert ssh_dir.exists
        assert ssh_dir.is_directory
        assert ssh_dir.mode == 0o700

    def test_ssh_keys_present(self, host, user_home):
        """Test that SSH keys are present."""
        # Look for any SSH private keys (common patterns)
        ssh_keys = host.run(
            f"find {user_home}/.ssh -name 'id_*' -not -name '*.pub' -type f"
        )

        # Should have at least one private key or the specific escemi key in CI
        escemi_key = host.file(f"{user_home}/.ssh/id_rsa_escemi")

        assert (
            ssh_keys.rc == 0 and ssh_keys.stdout.strip() or escemi_key.exists
        ), "At least one SSH private key should be present"

    def test_ssh_config_permissions(self, host, user_home):
        """Test SSH configuration file permissions."""
        ssh_config = host.file(f"{user_home}/.ssh/config")
        if ssh_config.exists:
            assert ssh_config.mode == 0o600

    def test_known_hosts_exists(self, host, user_home):
        """Test that known_hosts file exists if SSH keys are configured."""
        known_hosts = host.file(f"{user_home}/.ssh/known_hosts")
        # This file may or may not exist depending on usage, check permissions if exists
        if known_hosts.exists:
            assert known_hosts.mode in (0o644, 0o600)


class TestGpgKeys:
    """Test GPG keys configuration."""

    def test_gpg_directory_exists(self, host, user_home):
        """Test that .gnupg directory exists with proper permissions."""
        gnupg_dir = host.file(f"{user_home}/.gnupg")
        assert gnupg_dir.exists
        assert gnupg_dir.is_directory
        assert gnupg_dir.mode == 0o700

    def test_gpg_keys_present(self, host, target_user):
        """Test that GPG keys are present."""
        # Test GPG key listing - should have at least the pubring.kbx mentioned in CI
        gpg_list = host.run(f"sudo -u {target_user} gpg --list-keys")

        # Should either succeed and show keys, or at least have the pubring.kbx file
        pubring = host.file(f"/home/{target_user}/.gnupg/pubring.kbx")

        assert (
            gpg_list.rc == 0 or pubring.exists
        ), "GPG should be configured with keys or have pubring.kbx file"

    def test_gpg_configuration_files(self, host, user_home):
        """Test GPG configuration files exist and have proper permissions."""
        gpg_conf = host.file(f"{user_home}/.gnupg/gpg.conf")
        if gpg_conf.exists:
            assert gpg_conf.mode == 0o600

        gpg_agent_conf = host.file(f"{user_home}/.gnupg/gpg-agent.conf")
        if gpg_agent_conf.exists:
            assert gpg_agent_conf.mode == 0o600
