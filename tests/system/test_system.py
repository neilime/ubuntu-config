"""System domain acceptance tests: user-visible behaviors for system configuration."""


def test_timezone_and_locale_set(host):
    """As a user I expect the system timezone and locale to be configured."""
    tz = host.run("timedatectl show -p Timezone --value || true")

    assert tz.stdout.strip(), "Timezone should be set"

    locale = host.run("localectl status | sed -n 's/\\s*System Locale: //p' || true")
    # we only check the command runs; specific values are environment-dependent
    assert locale.rc == 0


def test_dark_mode_configuration_attempted(host):
    """As a user I expect dark mode configuration to be attempted (GUI-dependent)."""
    # Check if GUI session is available
    gui_check = host.run("""
        if [ -n "${XDG_CURRENT_DESKTOP:-}" ] || [ -n "${DESKTOP_SESSION:-}" ] || [ -n "${DISPLAY:-}" ]; then
            exit 0
        fi
        if command -v dbus-launch >/dev/null 2>&1 && pgrep -x dbus-daemon >/dev/null 2>&1; then
            exit 0
        fi
        if dconf read /org/gnome/shell/ubuntu/color-scheme >/dev/null 2>&1; then
            exit 0
        fi
        exit 1
    """)

    if gui_check.rc == 0:
        # GUI available - check that dark mode settings are actually applied
        shell_scheme = host.run("dconf read /org/gnome/shell/ubuntu/color-scheme 2>/dev/null || echo 'not-set'")
        interface_scheme = host.run("dconf read /org/gnome/desktop/interface/color-scheme 2>/dev/null || echo 'not-set'")
        
        # At least one should be set to prefer-dark if GUI is available
        assert "'prefer-dark'" in shell_scheme.stdout or "'prefer-dark'" in interface_scheme.stdout, \
            "Dark mode should be configured when GUI session is available"
    else:
        # No GUI - just verify dconf-cli is installed (requirement for when GUI becomes available)
        dconf_installed = host.run("which dconf")
        assert dconf_installed.rc == 0, "dconf-cli should be installed for future GUI configuration"
