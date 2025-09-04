"""Test Nix package manager setup."""

import pytest


def test_nix_directory_exists(host):
    """Test that Nix is installed."""
    nix_dir = host.file("/nix")
    assert nix_dir.exists, "/nix directory should exist"
    assert nix_dir.is_directory, "/nix should be a directory"


def test_nix_daemon_running(host):
    """Test that nix-daemon is running."""
    service = host.service("nix-daemon")
    assert service.is_running, "nix-daemon should be running"
    assert service.is_enabled, "nix-daemon should be enabled"


def test_nix_configuration_exists(host):
    """Test that Nix configuration is present."""
    nix_conf = host.file("/etc/nix/nix.conf")
    assert nix_conf.exists, "Nix configuration should exist"
    assert nix_conf.contains("experimental-features = nix-command flakes"), \
        "Nix should be configured with flakes support"


def test_nix_profile_setup(host):
    """Test that Nix profile script exists."""
    profile_script = host.file("/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh")
    assert profile_script.exists, "Nix profile script should exist"


def test_nix_command_available_for_user(host):
    """Test that nix command is available after sourcing profile."""
    cmd = host.run(". /nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh && which nix")
    assert cmd.rc == 0, "nix command should be available after sourcing profile"


def test_trusted_users_configured(host):
    """Test that trusted users are configured."""
    nix_conf = host.file("/etc/nix/nix.conf")
    assert nix_conf.contains("trusted-users"), \
        "Nix should have trusted users configured"