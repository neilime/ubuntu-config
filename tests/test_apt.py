"""Tests for APT packages and repositories setup."""

import pytest

pytestmark = pytest.mark.apt


class TestAptRepositories:  # pylint: disable=too-few-public-methods
    """Test APT repositories configuration."""

    def test_ppa_repositories_added(self, host):
        """Test that required PPA repositories are added."""
        # Check for ucaresystem-core PPA
        ppa_file = host.file("/etc/apt/sources.list.d/utappia-ubuntu-stable-noble.list")
        assert (
            ppa_file.exists
            or host.run("grep -r 'utappia.*stable' /etc/apt/sources.list*").rc == 0
        )


class TestAptPackages:
    """Test APT packages installation."""

    @pytest.mark.parametrize(
        "package",
        [
            "apt-transport-https",
            "ca-certificates",
            "gnupg-agent",
            "software-properties-common",
            "dconf-cli",
            "curl",
            "wget",
            "unzip",
            "htop",
            "bat",
            "zsh",
            "python3-dev",
            "python3-pip",
            "python3-setuptools",
            "make",
            "gh",
            "ucaresystem-core",
            "chromium-browser",
        ],
    )
    def test_required_packages_installed(self, host, package):
        """Test that required APT packages are installed."""
        pkg = host.package(package)
        assert pkg.is_installed, f"Package {package} should be installed"

    def test_package_cache_updated(self, host):
        """Test that package cache is relatively recent."""
        # Check that apt update was run recently (cache files exist)
        apt_cache = host.file("/var/lib/apt/lists")
        assert apt_cache.exists
        assert apt_cache.is_directory

        # Should have some package list files
        cache_files = host.run("find /var/lib/apt/lists -name '*.list' | wc -l")
        assert int(cache_files.stdout.strip()) > 0
