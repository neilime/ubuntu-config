"""User-config section normalization for the desired state schema."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state_support import (
    DesiredStateDefaultsSectionNormalizer,
)


# pylint: disable=too-few-public-methods
class UserConfigSectionNormalizer(DesiredStateDefaultsSectionNormalizer):
    """Normalize the user_config section of the desired-state schema."""

    def _normalize(
        self, config: dict[str, object], defaults: dict[str, object]
    ) -> dict[str, object]:
        user_config = self._resolver.mapping(
            config.get("user_config"), "ubuntu_config.user_config"
        )
        shell = self._resolver.mapping(
            user_config.get("shell"), "ubuntu_config.user_config.shell"
        )
        default_shell = self._resolver.mapping(
            defaults.get("shell"), "ubuntu_config.user_config.defaults.shell"
        )

        return {
            "files": self._resolver.list_value(
                self._resolver.value_or_default(
                    user_config.get("files"),
                    defaults.get("files"),
                ),
                "ubuntu_config.user_config.files",
            ),
            "shell": {
                "aliases": self._resolver.mapping(
                    self._resolver.value_or_default(
                        shell.get("aliases"),
                        default_shell.get("aliases"),
                    ),
                    "ubuntu_config.user_config.shell.aliases",
                ),
                "environment": self._resolver.mapping(
                    self._resolver.value_or_default(
                        shell.get("environment"),
                        default_shell.get("environment"),
                    ),
                    "ubuntu_config.user_config.shell.environment",
                ),
                "local_override_path": self._resolver.first_non_empty_string(
                    shell.get("local_override_path"),
                    default_shell.get("local_override_path"),
                ),
            },
        }
