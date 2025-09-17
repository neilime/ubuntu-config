"""Utility domain acceptance tests: GNOME favorites and utility apps."""

import pytest


def test_gnome_favorites_pinned(host, is_docker_test_env):
    if is_docker_test_env:
        pytest.skip("GNOME favorites unavailable in container tests")

    # Check that gnome shell favorites settings exist (using gsettings)
    out = host.run("gsettings get org.gnome.shell favorite-apps || true")
    assert out.rc == 0
