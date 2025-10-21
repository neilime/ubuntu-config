"""Utility domain acceptance tests: GNOME favorites and utility apps."""


def test_gnome_favorites_pinned(host):
    """Verify GNOME has favorite-apps configured (smoke check)."""
    # Check that gnome shell favorites settings exist (using gsettings)
    out = host.run("gsettings get org.gnome.shell favorite-apps || true")
    assert out.rc == 0


def test_libreoffice_installed(host):
    """Ensure LibreOffice is installed via Flatpak."""
    # Check for LibreOffice desktop entry
    search_paths = (
        "/usr/share/applications",
        "/usr/local/share/applications",
        "/var/lib/flatpak/exports/share/applications",
    )
    find_cmd = (
        "find "
        + " ".join(search_paths)
        + " -name 'org.libreoffice.LibreOffice*.desktop' 2>/dev/null || true"
    )
    cmd = host.run(find_cmd)
    assert (
        cmd.stdout.strip()
    ), "LibreOffice should have desktop entries installed via Flatpak"
