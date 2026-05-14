"""Desktop section normalization for the desired state schema."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state_support import (
    DesiredStateDefaultsSectionNormalizer,
)


# pylint: disable=too-few-public-methods
class DesktopSectionNormalizer(DesiredStateDefaultsSectionNormalizer):
    """Normalize the desktop section of the desired-state schema."""

    def _normalize(
        self, config: dict[str, object], defaults: dict[str, object]
    ) -> dict[str, object]:
        desktop = self._resolver.mapping(config.get("desktop"), "ubuntu_config.desktop")
        flatpak = self._resolver.mapping(
            desktop.get("flatpak"), "ubuntu_config.desktop.flatpak"
        )
        browser = self._resolver.mapping(
            desktop.get("browser"), "ubuntu_config.desktop.browser"
        )
        gnome = self._resolver.mapping(
            desktop.get("gnome"), "ubuntu_config.desktop.gnome"
        )
        default_flatpak = self._resolver.mapping(
            defaults.get("flatpak"), "ubuntu_config.desktop.defaults.flatpak"
        )
        default_browser = self._resolver.mapping(
            defaults.get("browser"), "ubuntu_config.desktop.defaults.browser"
        )
        default_gnome = self._resolver.mapping(
            defaults.get("gnome"), "ubuntu_config.desktop.defaults.gnome"
        )

        return {
            "flatpak": {
                "enabled": self._resolver.bool_value(
                    flatpak.get("enabled"),
                    self._resolver.bool_value(default_flatpak.get("enabled"), True),
                ),
                "remote": self._resolver.first_non_empty_string(
                    flatpak.get("remote"),
                    default_flatpak.get("remote"),
                ),
                "packages": self._resolver.list_value(
                    self._resolver.value_or_default(
                        flatpak.get("packages"),
                        default_flatpak.get("packages"),
                    ),
                    "ubuntu_config.desktop.flatpak.packages",
                ),
            },
            "browser": {
                "default": self._resolver.bool_value(
                    browser.get("default"),
                    self._resolver.bool_value(default_browser.get("default"), True),
                ),
                "profiles": self._resolver.list_value(
                    self._resolver.value_or_default(
                        browser.get("profiles"),
                        default_browser.get("profiles"),
                    ),
                    "ubuntu_config.desktop.browser.profiles",
                ),
                "policies": self._resolver.mapping(
                    self._resolver.value_or_default(
                        browser.get("policies"),
                        default_browser.get("policies"),
                    ),
                    "ubuntu_config.desktop.browser.policies",
                ),
            },
            "gnome": {
                "dark_mode": self._resolver.bool_value(
                    gnome.get("dark_mode"),
                    self._resolver.bool_value(default_gnome.get("dark_mode"), True),
                ),
                "favorites": self._resolver.list_value(
                    self._resolver.value_or_default(
                        gnome.get("favorites"),
                        default_gnome.get("favorites"),
                    ),
                    "ubuntu_config.desktop.gnome.favorites",
                ),
            },
        }
