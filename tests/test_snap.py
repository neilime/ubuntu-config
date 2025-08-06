"""Tests for snap packages."""

import pytest

pytestmark = pytest.mark.snap


class TestSnapSystem:
    """Test Snap package system."""

    def test_snapd_installed(self, host):
        """Test that snapd is installed."""
        snapd = host.package("snapd")
        assert snapd.is_installed

    def test_snapd_service_running(self, host):
        """Test that snapd service is running."""
        snapd_service = host.service("snapd")
        assert snapd_service.is_running

    def test_snap_command_available(self, host):
        """Test that snap command is available."""
        snap_cmd = host.run("snap --version")
        assert snap_cmd.rc == 0
        assert "snap" in snap_cmd.stdout.lower()


class TestSnapPackages:
    """Test snap packages installation."""

    def test_snap_list_command(self, host):
        """Test that snap list command works."""
        snap_list = host.run("snap list")
        assert snap_list.rc == 0

        # Should at least have core snap
        assert "core" in snap_list.stdout or "snapd" in snap_list.stdout

    def test_common_snap_packages(self, host):
        """Test common snap packages that might be installed."""
        # These are packages that might be installed based on the configuration
        possible_packages = [
            "code",  # Visual Studio Code
            "discord",
            "slack",
            "spotify",
            "bitwarden",
        ]

        snap_list = host.run("snap list")
        installed_snaps = snap_list.stdout.lower()

        # We don't require specific snaps, but if installed, they should be valid
        for package in possible_packages:
            if package in installed_snaps:
                # If a snap is installed, verify it's properly installed
                snap_info = host.run(f"snap info {package}")
                assert snap_info.rc == 0, f"Snap {package} should have valid info"

    def test_snap_core_functionality(self, host):
        """Test core snap functionality."""
        # Test that snap can refresh (even if it says nothing to do)
        snap_refresh = host.run("snap refresh --list")
        # This should either show updates available or "All snaps up to date"
        assert snap_refresh.rc == 0


class TestSnapConfiguration:
    """Test snap configuration and permissions."""

    def test_snap_mount_points(self, host):
        """Test that snap mount points exist."""
        snap_dir = host.file("/snap")
        assert snap_dir.exists
        assert snap_dir.is_directory

    def test_snap_bin_in_path(self, host):
        """Test that snap bin directory is in PATH."""
        path_cmd = host.run("echo $PATH")
        assert "/snap/bin" in path_cmd.stdout

    def test_snap_user_data(self, host, user_home):
        """Test snap user data directory."""
        snap_user_data = host.file(f"{user_home}/snap")
        # This directory may or may not exist depending on snap usage
        if snap_user_data.exists:
            assert snap_user_data.is_directory
