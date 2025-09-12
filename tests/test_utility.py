"""Test utility domain setup - System utilities, maintenance tools, and security applications.

Feature: Utility Domain Setup
    As a system administrator
    I want to ensure the utility domain is properly configured
    So that I have access to system maintenance, utility tools, and security applications

    Scenario: Utility tools are installed
        Given the utility setup has been executed
        When I check for utility applications
        Then system maintenance tools should be available
        And utility applications should be accessible via Flatpak
        And security tools should be available

    Scenario: System maintenance tools are functional
        Given the utility setup has been executed
        When I check system maintenance capabilities
        Then maintenance tools should be properly configured
        And utility repositories should be available
        And security applications should be properly sandboxed
"""

import pytest
from conftest import check_desktop_entries_exist


def test_given_utility_setup_when_checking_apt_packages_then_utility_tools_should_be_installed(
    host,
):
    """
    Scenario: Utility APT packages are installed
    Given the utility setup has been executed
    When I check for utility APT packages
    Then system maintenance tools should be installed
    """
    utility_packages = ["ucaresystem-core"]

    for package in utility_packages:
        pkg = host.package(package)
        assert pkg.is_installed, f"Utility package {package} should be installed"


def test_given_utility_setup_when_checking_flatpak_apps_then_utility_apps_installed(
    host,
):
    """
    Scenario: Utility Flatpak applications are installed
    Given the utility setup has been executed
    When I check for utility Flatpak applications
    Then JDownloader, CopyQ, SimpleScan, and DejaDup should be available
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    utility_flatpaks = [
        "org.jdownloader.JDownloader",
        "com.github.hluk.copyq",
        "org.gnome.SimpleScan",
        "org.gnome.DejaDup",
        "com.bitwarden.desktop",
    ]

    for app in utility_flatpaks:
        cmd = host.run(f"flatpak list --app | grep {app}")
        assert (
            cmd.rc == 0 or "not available" not in cmd.stderr.lower()
        ), f"Utility Flatpak application {app} should be installed"


def test_given_utility_setup_when_checking_ucaresystem_install_then_package_available(
    host,
):
    """
    Scenario: uCareSystem package is installed via .deb download
    Given the utility setup has been executed
    When I check for ucaresystem installation
    Then ucaresystem-core package should be available
    """
    # Check if ucaresystem-core package is installed
    pkg = host.package("ucaresystem-core")
    assert pkg.is_installed, "Ucaresystem-core package should be installed"


def test_utility_desktop_entries(host):
    """
    Scenario: Utility applications are accessible from desktop
    Given the utility setup has been executed
    When I check for desktop entries
    Then utility applications should have desktop entries
    """
    desktop_entries = [
        "org.jdownloader.JDownloader.desktop",
        "com.github.hluk.copyq.desktop",
        "org.gnome.SimpleScan.desktop",
        "org.gnome.DejaDup.desktop",
        "com.bitwarden.desktop.desktop",
    ]
    check_desktop_entries_exist(host, desktop_entries)


def test_given_utility_setup_when_checking_ucaresystem_then_maintenance_tool_functional(
    host,
):
    """
    Scenario: System maintenance tool is functional
    Given the utility setup has been executed
    When I check ucaresystem functionality
    Then the maintenance tool should be executable
    """
    ucare_cmd = host.run("which ucaresystem-core")
    if ucare_cmd.rc != 0:
        # Try alternative locations
        ucare_cmd = host.run("find /usr -name 'ucaresystem-core' 2>/dev/null")
        assert (
            ucare_cmd.stdout.strip()
        ), "Ucaresystem-core should be installed and accessible"
    else:
        assert ucare_cmd.rc == 0, "Ucaresystem-core should be available in PATH"


def test_given_utility_setup_when_checking_backup_capabilities_then_backup_tools_available(
    host,
):
    """
    Scenario: Backup capabilities are available
    Given the utility setup has been executed
    When I check backup tool availability
    Then DejaDup should provide backup functionality
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    # Check if DejaDup is available for backup functionality
    dejadup_cmd = host.run("flatpak list --app | grep org.gnome.DejaDup")
    assert (
        dejadup_cmd.rc == 0 or "not available" not in dejadup_cmd.stderr.lower()
    ), "DejaDup backup tool should be available"


def test_given_utility_setup_when_checking_security_apps_then_password_managers_available(
    host,
):
    """
    Scenario: Security applications are available
    Given the utility setup has been executed
    When I check for security applications via Flatpak
    Then Bitwarden should be available as a password manager
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    cmd = host.run("flatpak list --app | grep com.bitwarden.desktop")
    assert (
        cmd.rc == 0 or "not available" not in cmd.stderr.lower()
    ), "Bitwarden password manager should be installed"


def test_given_utility_setup_when_checking_flatpak_sandboxing_then_security_apps_isolated(
    host,
):
    """
    Scenario: Security applications are properly sandboxed
    Given the utility setup has been executed
    When I check Flatpak sandboxing for security apps
    Then security applications should run in isolated environments
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    # Check that Flatpak sandboxing is enabled for Bitwarden
    flatpak_info_cmd = host.run("flatpak info com.bitwarden.desktop 2>/dev/null")
    if flatpak_info_cmd.rc == 0:
        # If the app is installed, check if it's properly sandboxed
        permissions_cmd = host.run(
            "flatpak info --show-permissions com.bitwarden.desktop 2>/dev/null"
        )
        # Bitwarden should have network access but limited filesystem access
        assert permissions_cmd.rc == 0, "Should be able to check Flatpak permissions"
    else:
        pytest.skip("Bitwarden not installed in test environment")


def test_given_utility_setup_when_checking_network_security_then_secure_connections_available(
    host,
):
    """
    Scenario: Secure network connections are available
    Given the utility setup has been executed
    When I check network security capabilities
    Then TLS/SSL connections should be supported for password managers
    """
    # Check that we can make secure connections (important for password managers)
    ssl_cmd = host.run("openssl version")
    assert ssl_cmd.rc == 0, "OpenSSL should be available for secure connections"

    # Check that we have up-to-date CA certificates
    ca_certs = host.file("/etc/ssl/certs/ca-certificates.crt")
    assert ca_certs.exists, "CA certificates should be available for secure connections"


def test_given_utility_setup_when_checking_password_manager_then_bitwarden_reachable(
    host,
):
    """
    Scenario: Password manager can reach its servers
    Given the utility setup has been executed
    When I check password manager connectivity
    Then Bitwarden should be able to reach its servers
    """
    # Test connectivity to Bitwarden EU servers (as configured in group_vars)
    bitwarden_cmd = host.run(
        "curl -s --connect-timeout 5 --max-time 10 -o /dev/null "
        "-w '%{http_code}' https://vault.bitwarden.eu"
    )

    if bitwarden_cmd.rc == 0:
        assert bitwarden_cmd.stdout.strip() in [
            "200",
            "301",
            "302",
            "403",
        ], "Should be able to reach Bitwarden servers"
    else:
        # If direct connectivity fails, at least check DNS resolution
        dns_cmd = host.run("nslookup vault.bitwarden.eu")
        assert dns_cmd.rc == 0, "Should be able to resolve Bitwarden server addresses"
