"""Secrets section normalization for the desired state schema."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state_support import (
    DesiredStateDefaultsSectionNormalizer,
)


# pylint: disable=too-few-public-methods
class SecretsSectionNormalizer(DesiredStateDefaultsSectionNormalizer):
    """Normalize the secrets section of the desired-state schema."""

    def _normalize(
        self, config: dict[str, object], defaults: dict[str, object]
    ) -> dict[str, object]:
        secrets = self._resolver.mapping(config.get("secrets"), "ubuntu_config.secrets")
        bitwarden = self._resolver.mapping(
            secrets.get("bitwarden"), "ubuntu_config.secrets.bitwarden"
        )
        default_bitwarden = self._resolver.mapping(
            defaults.get("bitwarden"), "ubuntu_config.secrets.defaults.bitwarden"
        )

        return {
            "enabled": self._resolver.bool_value(
                secrets.get("enabled"),
                self._resolver.bool_value(defaults.get("enabled"), False),
            ),
            "provider": self._resolver.first_non_empty_string(
                secrets.get("provider"), defaults.get("provider")
            ),
            "bitwarden": {
                "server": self._resolver.first_non_empty_string(
                    bitwarden.get("server"),
                    default_bitwarden.get("server"),
                ),
                "ssh_keys": self._resolver.list_value(
                    self._resolver.value_or_default(
                        bitwarden.get("ssh_keys"),
                        default_bitwarden.get("ssh_keys"),
                    ),
                    "ubuntu_config.secrets.bitwarden.ssh_keys",
                ),
                "gpg_keys": self._resolver.list_value(
                    self._resolver.value_or_default(
                        bitwarden.get("gpg_keys"),
                        default_bitwarden.get("gpg_keys"),
                    ),
                    "ubuntu_config.secrets.bitwarden.gpg_keys",
                ),
                "browser_recovery_items": self._resolver.list_value(
                    self._resolver.value_or_default(
                        bitwarden.get("browser_recovery_items"),
                        default_bitwarden.get("browser_recovery_items"),
                    ),
                    "ubuntu_config.secrets.bitwarden.browser_recovery_items",
                ),
            },
        }
