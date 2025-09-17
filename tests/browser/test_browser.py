"""Browser domain acceptance tests: user flows around browsers and links."""

import pytest


def test_can_launch_chromium_from_desktop(host, is_docker_test_env):
    if is_docker_test_env:
        pytest.skip("Desktop not available in container tests")

    # Check for Chromium desktop entry as proxy for launchbar availability
    cmd = host.run(
        "find /usr/share/applications /usr/local/share/applications /var/lib/flatpak/exports/share/applications -name 'chromium*.desktop' 2>/dev/null || true"
    )
    assert (
        cmd.stdout.strip()
    ), "Chromium should have a desktop entry to be launchable from the launchbar"


def test_default_browser_is_chromium(host, is_docker_test_env):
    if is_docker_test_env:
        pytest.skip("xdg defaults unreliable in containers")

    out = host.run("xdg-settings get default-web-browser || true")
    assert out.rc == 0
    val = out.stdout.strip()
    assert any(
        k in val for k in ("chromium", "Chromium", "brave")
    ), "Default browser should be a Chromium-based browser"
