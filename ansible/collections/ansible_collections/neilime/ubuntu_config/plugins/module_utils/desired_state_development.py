"""Development section normalization for the desired state schema."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state_support import (
    DesiredStateDefaultsSectionNormalizer,
)


# pylint: disable=too-few-public-methods
class DevelopmentSectionNormalizer(DesiredStateDefaultsSectionNormalizer):
    """Normalize the development section of the desired-state schema."""

    def _normalize(
        self, config: dict[str, object], defaults: dict[str, object]
    ) -> dict[str, object]:
        development = self._resolver.mapping(
            config.get("development"), "ubuntu_config.development"
        )
        git = self._resolver.mapping(
            development.get("git"), "ubuntu_config.development.git"
        )
        signing = self._resolver.mapping(
            git.get("signing"), "ubuntu_config.development.git.signing"
        )
        default_git = self._resolver.mapping(
            defaults.get("git"), "ubuntu_config.development.defaults.git"
        )
        default_signing = self._resolver.mapping(
            default_git.get("signing"),
            "ubuntu_config.development.defaults.git.signing",
        )

        return {
            "packages": self._resolver.list_value(
                self._resolver.value_or_default(
                    development.get("packages"),
                    defaults.get("packages"),
                ),
                "ubuntu_config.development.packages",
            ),
            "editor_packages": self._resolver.list_value(
                self._resolver.value_or_default(
                    development.get("editor_packages"),
                    defaults.get("editor_packages"),
                ),
                "ubuntu_config.development.editor_packages",
            ),
            "git": {
                "default_branch": self._resolver.first_non_empty_string(
                    git.get("default_branch"),
                    default_git.get("default_branch"),
                ),
                "editor": self._resolver.first_non_empty_string(
                    git.get("editor"), default_git.get("editor")
                ),
                "signing": {
                    "enabled": self._resolver.bool_value(
                        signing.get("enabled"),
                        self._resolver.bool_value(
                            default_signing.get("enabled"), False
                        ),
                    )
                },
            },
            "runtimes": self._resolver.mapping(
                self._resolver.value_or_default(
                    development.get("runtimes"),
                    defaults.get("runtimes"),
                ),
                "ubuntu_config.development.runtimes",
            ),
        }
