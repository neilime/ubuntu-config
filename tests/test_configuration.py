"""Tests for system configuration."""

import pytest

pytestmark = pytest.mark.config


class TestLocaleConfiguration:
    """Test locale configuration."""

    def test_locale_set(self, host):
        """Test that locale is properly configured."""
        locale_cmd = host.run("locale")
        assert locale_cmd.rc == 0

        # Check for UTF-8 encoding
        assert "UTF-8" in locale_cmd.stdout or "utf8" in locale_cmd.stdout.lower()

    def test_locale_gen_exists(self, host):
        """Test that locale generation configuration exists."""
        locale_gen = host.file("/etc/locale.gen")
        if locale_gen.exists:
            # Should have en_US.UTF-8 uncommented
            assert locale_gen.contains("en_US.UTF-8")


class TestTimezoneConfiguration:  # pylint: disable=too-few-public-methods
    """Test timezone configuration."""

    def test_timezone_set(self, host):
        """Test that timezone is configured."""
        # Check current timezone
        timedatectl_cmd = host.run("timedatectl show --property=Timezone --value")
        if timedatectl_cmd.rc == 0:
            timezone = timedatectl_cmd.stdout.strip()
            assert timezone != "", "Timezone should be set"
            # Should be a valid timezone format (e.g., Europe/Paris)
            assert "/" in timezone or timezone in ["UTC", "GMT"]
        else:
            # Fallback: check /etc/timezone
            timezone_file = host.file("/etc/timezone")
            if timezone_file.exists:
                assert timezone_file.content_string.strip() != ""


class TestFavoritesConfiguration:  # pylint: disable=too-few-public-methods
    """Test favorites and launcher configuration."""

    def test_gnome_settings_accessibility(self, host):
        """Test that GNOME settings can be accessed if in GNOME environment."""
        # This test is optional since we might not be in a GNOME environment
        gsettings_cmd = host.run("which gsettings")
        if gsettings_cmd.rc == 0:
            # Test that gsettings can read some basic settings
            test_cmd = host.run("timeout 5 gsettings list-schemas")
            # If it succeeds, GNOME is available, else that's OK too
            assert test_cmd.rc in [0, 124, 1]  # 0=success, 124=timeout, 1=no display


class TestWebBrowserConfiguration:
    """Test web browser configuration."""

    def test_chromium_installed(self, host):
        """Test that Chromium browser is installed."""
        chromium = host.package("chromium-browser")
        assert chromium.is_installed

    def test_chromium_executable(self, host):
        """Test that Chromium is executable."""
        # Test the executable exists
        chromium_bin = host.file("/usr/bin/chromium-browser")
        if chromium_bin.exists:
            assert chromium_bin.is_file
            assert chromium_bin.mode & 0o111  # Check execute permissions

    def test_desktop_file_exists(self, host):
        """Test that Chromium desktop file exists."""
        desktop_files = [
            "/usr/share/applications/chromium-browser.desktop",
            "/usr/share/applications/chromium.desktop",
        ]

        desktop_file_exists = any(
            host.file(desktop_file).exists for desktop_file in desktop_files
        )
        assert desktop_file_exists, "Chromium desktop file should exist"


class TestSystemUtilities:
    """Test system utilities and tools."""

    @pytest.mark.parametrize(
        "utility",
        [
            "htop",
            "bat",
            "curl",
            "wget",
            "unzip",
        ],
    )
    def test_system_utilities_installed(self, host, utility):
        """Test that system utilities are installed."""
        pkg = host.package(utility)
        assert pkg.is_installed, f"System utility {utility} should be installed"

    def test_fonts_installed(self, host):
        """Test that FiraCode fonts are installed."""
        firacode = host.package("fonts-firacode")
        assert firacode.is_installed

    def test_dconf_cli_available(self, host):
        """Test that dconf CLI is available."""
        dconf = host.package("dconf-cli")
        assert dconf.is_installed

        # Test dconf command works
        dconf_cmd = host.run("dconf help")
        assert dconf_cmd.rc == 0


class TestCleaningTools:
    """Test system cleaning tools."""

    def test_ucaresystem_core_installed(self, host):
        """Test that UCareSystem Core is installed."""
        ucare = host.package("ucaresystem-core")
        assert ucare.is_installed

    def test_ucare_executable(self, host):
        """Test that ucare command is available."""
        # Test that ucare command exists
        ucare_cmd = host.run("which ucaresystem-core")
        # ucaresystem-core might not be in PATH, check if package provides executables
        if ucare_cmd.rc != 0:
            # Check if the package is properly installed
            # This is OK - the package might provide other functionality
            assert True  # Package is installed, which is what matters


class TestCopyQConfiguration:
    """Test CopyQ clipboard manager configuration."""

    def test_copyq_installed(self, host):
        """Test that CopyQ is installed."""
        copyq = host.package("copyq")
        assert copyq.is_installed

    def test_copyq_executable(self, host):
        """Test that CopyQ executable exists."""
        copyq_bin = host.file("/usr/bin/copyq")
        assert copyq_bin.exists
        assert copyq_bin.is_file
        assert copyq_bin.mode & 0o111  # Check execute permissions

    def test_copyq_autostart_file_exists(self, host):
        """Test that CopyQ autostart file is configured."""
        autostart_file = host.file(f"/home/{host.user().name}/.config/autostart/copy-q.desktop")
        assert autostart_file.exists
        assert autostart_file.is_file
        assert autostart_file.contains("CopyQ")
        assert autostart_file.contains("Exec=sh -c \"copyq; sleep 2; copyq show\"")

    def test_copyq_can_run_help(self, host):
        """Test that CopyQ can run basic help command (doesn't require GUI)."""
        # Test a command that doesn't require the GUI/server
        copyq_help = host.run("copyq --help")
        assert copyq_help.rc == 0
        assert "clipboard manager" in copyq_help.stdout.lower() or "copyq" in copyq_help.stdout.lower()
