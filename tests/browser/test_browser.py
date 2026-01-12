"""Browser domain acceptance tests: user flows around browsers and links."""


def test_can_launch_chromium_from_desktop(host, find_desktop_entries):
    """Ensure a Chromium desktop entry exists so the launchbar can start it."""
    # Check for Chromium desktop entry as proxy for launchbar availability
    entries = find_desktop_entries(host, "chromium*.desktop")
    assert (
        entries
    ), "Chromium should have a desktop entry to be launchable from the launchbar"


def test_default_browser_is_chromium(host):
    """Check the user's default web browser is Chromium-based."""
    out = host.run("xdg-settings get default-web-browser || true")
    assert out.rc == 0
    val = out.stdout.strip()
    assert any(
        k in val for k in ("chromium", "Chromium", "brave")
    ), "Default browser should be a Chromium-based browser"
