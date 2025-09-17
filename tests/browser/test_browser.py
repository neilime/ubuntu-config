"""Browser domain acceptance tests: user flows around browsers and links."""


def test_can_launch_chromium_from_desktop(host):
    # Check for Chromium desktop entry as proxy for launchbar availability
    cmd = host.run(
        "find /usr/share/applications /usr/local/share/applications /var/lib/flatpak/exports/share/applications -name 'chromium*.desktop' 2>/dev/null || true"
    )
    assert (
        cmd.stdout.strip()
    ), "Chromium should have a desktop entry to be launchable from the launchbar"


def test_default_browser_is_chromium(host):
    out = host.run("xdg-settings get default-web-browser || true")
    assert out.rc == 0
    val = out.stdout.strip()
    assert any(
        k in val for k in ("chromium", "Chromium", "brave")
    ), "Default browser should be a Chromium-based browser"
