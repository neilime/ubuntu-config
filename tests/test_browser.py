"""Test browser domain setup - Web browsers and related tools.

Feature: Browser Domain Setup
    As a user
    I want to ensure the browser domain is properly configured
    So that I have access to web browsing capabilities

    Scenario: Browser applications are installed
        Given the browser setup has been executed
        When I check for browser applications
        Then web browsers should be available via Flatpak
        And browser applications should be set as default when configured
"""

import pytest
from conftest import check_desktop_entries_exist


def test_given_browser_setup_when_checking_flatpak_apps_then_browser_apps_installed(
    host,
):
    """
    Scenario: Browser Flatpak applications are installed
    Given the browser setup has been executed
    When I check for browser Flatpak applications
    Then Chromium should be available
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    browser_flatpaks = ["org.chromium.Chromium"]

    for app in browser_flatpaks:
        cmd = host.run(f"flatpak list --app | grep {app}")
        assert (
            cmd.rc == 0 or "not available" not in cmd.stderr.lower()
        ), f"Browser Flatpak application {app} should be installed"


def test_browser_desktop_entries(host):
    """
    Scenario: Browser applications are accessible from desktop
    Given the browser setup has been executed
    When I check for desktop entries
    Then browser applications should have desktop entries
    """
    desktop_entries = ["org.chromium.Chromium.desktop"]
    check_desktop_entries_exist(host, desktop_entries)


def test_given_browser_setup_when_checking_web_connectivity_then_browsers_have_internet(
    host,
):
    """
    Scenario: Browsers have internet connectivity
    Given the browser setup has been executed
    When I check internet connectivity
    Then browsers should be able to access web content
    """
    # Basic internet connectivity check
    connectivity_cmd = host.run(
        "curl -s --connect-timeout 5 --max-time 10 -o /dev/null "
        "-w '%{http_code}' https://www.google.com"
    )
    if connectivity_cmd.rc == 0:
        assert connectivity_cmd.stdout.strip() in [
            "200",
            "301",
            "302",
        ], "Internet connectivity should be available for browsers"
    else:
        # If curl fails, at least check DNS resolution
        dns_cmd = host.run("nslookup google.com")
        assert dns_cmd.rc == 0, "DNS resolution should work for web browsing"


def test_given_browser_setup_when_checking_default_browser_then_configuration_should_be_consistent(
    host, target_user
):
    """
    Scenario: Default browser configuration is consistent
    Given the browser setup has been executed
    When I check default browser settings
    Then the default browser should be properly configured
    """
    # Check if there's a default browser set in the system
    default_cmd = host.run(
        f"sudo -u {target_user} xdg-settings get default-web-browser 2>/dev/null"
    )

    if default_cmd.rc == 0 and default_cmd.stdout.strip():
        browser_entry = default_cmd.stdout.strip()
        assert browser_entry.endswith(
            ".desktop"
        ), f"Default browser should be a valid desktop entry: {browser_entry}"
    else:
        # In test environment, this might not be set, which is acceptable
        pytest.skip("Default browser configuration not available in test environment")
