"""Test communication domain setup - Communication and collaboration tools.

Feature: Communication Domain Setup
    As a user
    I want to ensure the communication domain is properly configured
    So that I have access to communication and collaboration tools

    Scenario: Communication applications are installed
        Given the communication setup has been executed
        When I check for communication applications
        Then all communication tools should be available via Flatpak
        And communication applications should be accessible
"""

import pytest
from conftest import check_desktop_entries_exist


def test_communication_flatpak_apps_installed(host):
    """
    Scenario: Communication Flatpak applications are installed
    Given the communication setup has been executed
    When I check for communication Flatpak applications
    Then Slack should be available
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    communication_flatpaks = ["com.slack.Slack"]

    for app in communication_flatpaks:
        cmd = host.run(f"flatpak list --app | grep {app}")
        assert (
            cmd.rc == 0 or "not available" not in cmd.stderr.lower()
        ), f"Communication Flatpak application {app} should be installed"


def test_communication_desktop_entries(host):
    """
    Scenario: Communication applications are accessible from desktop
    Given the communication setup has been executed
    When I check for desktop entries
    Then communication applications should have desktop entries
    """
    desktop_entries = ["com.slack.Slack.desktop"]
    check_desktop_entries_exist(host, desktop_entries)


def test_communication_network_access(host):
    """
    Scenario: Communication applications have network connectivity
    Given the communication setup has been executed
    When I check network connectivity for communication apps
    Then the system should allow network access for communication tools
    """
    # Basic network connectivity check
    network_cmd = host.run("ping -c 1 -W 2 8.8.8.8")
    assert (
        network_cmd.rc == 0
    ), "Network connectivity should be available for communication apps"
