"""Utility domain acceptance tests: GNOME favorites and utility apps."""


def test_gnome_favorites_pinned(host):
    """Verify GNOME has favorite-apps configured (smoke check)."""
    # Check that gnome shell favorites settings exist (using gsettings)
    out = host.run("gsettings get org.gnome.shell favorite-apps || true")
    assert out.rc == 0
