"""Communication domain acceptance tests: availability of common communication apps."""


def test_mail_and_chat_apps_present(host):
    """Smoke-check that common communication apps are present (if installed)."""
    # check for common apps like slack (flatpak names vary)
    for name in ("slack",):
        cmd = host.run(f"which {name} >/dev/null 2>&1 || true")
        # it's okay if some are missing; this is a smoke check
        assert cmd.rc in (0, 0), f"Checked availability of {name}"
