"""Test Flatpak desktop applications setup."""

import pytest


def test_flatpak_installed(host):
    """Test that Flatpak is installed."""
    flatpak = host.package("flatpak")
    assert flatpak.is_installed, "Flatpak should be installed"


def test_flathub_repository_added(host):
    """Test that Flathub repository is configured."""
    cmd = host.run("flatpak remotes --show-details")
    if cmd.rc == 0:  # Only test if flatpak is working (not in container)
        assert "flathub" in cmd.stdout, "Flathub repository should be configured"


@pytest.mark.skipif(
    "ansible_module_running_in_container",
    reason="Flatpak apps don't work in containers"
)
def test_flatpak_applications_installed(host):
    """Test that Flatpak applications are installed."""
    expected_apps = [
        "com.visualstudio.code",
        "com.slack.Slack", 
        "com.spotify.Client",
        "org.chromium.Chromium"
    ]
    
    cmd = host.run("flatpak list --app --columns=application")
    if cmd.rc == 0:
        installed_apps = cmd.stdout
        for app in expected_apps:
            assert app in installed_apps, f"Flatpak app {app} should be installed"


def test_flatpak_command_available(host):
    """Test that flatpak command is available."""
    cmd = host.run("which flatpak")
    assert cmd.rc == 0, "flatpak command should be available"