"""System section normalization for the desired state schema."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state_support import (
    DesiredStateValueResolver,
)


# pylint: disable=too-few-public-methods
class SystemSectionNormalizer:
    """Normalize the system section of the desired-state schema."""

    def __init__(self, resolver: DesiredStateValueResolver) -> None:
        self._resolver = resolver

    def normalize(
        self,
        config: dict[str, object],
        environment: dict[str, str],
        defaults: dict[str, object],
    ) -> dict[str, object]:
        """Return the normalized system section."""

        system = self._resolver.mapping(config.get("system"), "ubuntu_config.system")
        packages = self._resolver.mapping(
            system.get("packages"), "ubuntu_config.system.packages"
        )
        repositories = self._resolver.mapping(
            system.get("repositories"), "ubuntu_config.system.repositories"
        )
        services = self._resolver.mapping(
            system.get("services"), "ubuntu_config.system.services"
        )
        settings = self._resolver.mapping(
            system.get("settings"), "ubuntu_config.system.settings"
        )
        default_packages = self._resolver.mapping(
            defaults.get("packages"), "ubuntu_config.system.defaults.packages"
        )
        default_cache_valid_time = self._resolver.int_value(
            default_packages.get("cache_valid_time"), 86400
        )
        default_repositories = self._resolver.mapping(
            defaults.get("repositories"),
            "ubuntu_config.system.defaults.repositories",
        )
        default_services = self._resolver.mapping(
            defaults.get("services"),
            "ubuntu_config.system.defaults.services",
        )
        default_settings = self._resolver.mapping(
            defaults.get("settings"), "ubuntu_config.system.defaults.settings"
        )

        return {
            "state_dir": self._resolver.first_non_empty_string(
                environment.get("UBUNTU_CONFIG_SYSTEM_STATE_DIR"),
                system.get("state_dir"),
                defaults.get("state_dir"),
            ),
            "locale": self._resolver.first_non_empty_string(
                system.get("locale"),
                defaults.get("locale"),
            ),
            "timezone": self._resolver.first_non_empty_string(
                system.get("timezone"),
                defaults.get("timezone"),
            ),
            "packages": {
                "prerequisites": self._resolver.list_value(
                    self._resolver.value_or_default(
                        packages.get("prerequisites"),
                        default_packages.get("prerequisites"),
                    ),
                    "ubuntu_config.system.packages.prerequisites",
                ),
                "apt": self._resolver.list_value(
                    self._resolver.value_or_default(
                        packages.get("apt"),
                        default_packages.get("apt"),
                    ),
                    "ubuntu_config.system.packages.apt",
                ),
                "cache_valid_time": self._resolver.int_value(
                    packages.get("cache_valid_time"), default_cache_valid_time
                ),
            },
            "repositories": {
                "apt": self._resolver.list_value(
                    self._resolver.value_or_default(
                        repositories.get("apt"),
                        default_repositories.get("apt"),
                    ),
                    "ubuntu_config.system.repositories.apt",
                ),
            },
            "directories": self._resolver.list_value(
                self._resolver.value_or_default(
                    system.get("directories"),
                    defaults.get("directories"),
                ),
                "ubuntu_config.system.directories",
            ),
            "services": {
                "enabled": self._resolver.list_value(
                    self._resolver.value_or_default(
                        services.get("enabled"),
                        default_services.get("enabled"),
                    ),
                    "ubuntu_config.system.services.enabled",
                ),
                "disabled": self._resolver.list_value(
                    self._resolver.value_or_default(
                        services.get("disabled"),
                        default_services.get("disabled"),
                    ),
                    "ubuntu_config.system.services.disabled",
                ),
            },
            "settings": {
                "sysctl": self._resolver.mapping(
                    self._resolver.value_or_default(
                        settings.get("sysctl"),
                        default_settings.get("sysctl"),
                    ),
                    "ubuntu_config.system.settings.sysctl",
                ),
            },
        }
