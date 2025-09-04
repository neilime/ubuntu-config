"""Test base system setup (host layer)."""

import pytest


def test_essential_packages_installed(host):
    """Test that essential system packages are installed."""
    essential_packages = [
        "apt-transport-https",
        "ca-certificates",
        "gnupg-agent",
        "software-properties-common",
        "curl",
        "wget",
        "unzip",
        "htop",
        "cron"
    ]
    
    for package in essential_packages:
        pkg = host.package(package)
        assert pkg.is_installed, f"Package {package} should be installed"


def test_system_services_running(host):
    """Test that essential system services are running."""
    services = ["cron"]
    
    for service in services:
        svc = host.service(service)
        assert svc.is_running, f"Service {service} should be running"
        assert svc.is_enabled, f"Service {service} should be enabled"


def test_apt_update_recent(host):
    """Test that apt cache is reasonably recent."""
    cmd = host.run("find /var/lib/apt/lists -name '*Packages*' -mtime -1")
    assert cmd.rc == 0
    assert len(cmd.stdout.strip()) > 0, "APT cache should be recent"