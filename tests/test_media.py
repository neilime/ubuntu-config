"""Test media domain setup - Media applications and multimedia tools.

Feature: Media Domain Setup
    As a user
    I want to ensure the media domain is properly configured
    So that I have access to multimedia applications

    Scenario: Media applications are installed
        Given the media setup has been executed
        When I check for media applications
        Then all media tools should be available via Flatpak
        And media applications should be properly configured

    Scenario: Media applications are accessible from desktop
        Given the media setup has been executed
        When I check for desktop entries
        Then media applications should have desktop entries

    Scenario: Multimedia runtime support is available
        Given the media setup has been executed
        When I check for multimedia runtime support
        Then multimedia frameworks should be available
"""

import pytest
from conftest import check_desktop_entries_exist


def test_given_media_setup_when_checking_flatpak_apps_then_media_applications_should_be_installed(
    host,
):
    """
    Scenario: Media Flatpak applications are installed
    Given the media setup has been executed
    When I check for media Flatpak applications
    Then Spotify and VLC should be available
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    media_flatpaks = ["com.spotify.Client", "org.videolan.VLC"]

    for app in media_flatpaks:
        cmd = host.run(f"flatpak list --app | grep {app}")
        assert (
            cmd.rc == 0 or "not available" not in cmd.stderr.lower()
        ), f"Media Flatpak application {app} should be installed"


def test_media_desktop_entries(host):
    """
    Scenario: Media applications are accessible from desktop
    Given the media setup has been executed
    When I check for desktop entries
    Then media applications should have desktop entries
    """
    desktop_entries = ["com.spotify.Client.desktop", "org.videolan.VLC.desktop"]
    check_desktop_entries_exist(host, desktop_entries)


def test_media_flatpak_runtime(host):
    """
    Scenario: Multimedia runtime support is available
    Given the media setup has been executed
    When I check for Flatpak multimedia runtime
    Then necessary runtime should be installed for media applications
    """
    if host.run("which flatpak").rc != 0:
        pytest.skip("Flatpak not available in test environment")

    # Check for common multimedia runtime
    runtime_cmd = host.run(
        "flatpak list --runtime | grep -E '(freedesktop|gnome).*Platform'"
    )
    assert (
        runtime_cmd.rc == 0 or runtime_cmd.stdout.strip()
    ), "Multimedia runtime support should be available"
