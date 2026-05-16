"""Support classes for desired state normalization."""

from __future__ import annotations

from copy import deepcopy


# pylint: disable=too-few-public-methods
class DesiredStateValueResolver:
    """Validate and clone schema values used by section normalizers."""

    @staticmethod
    def bool_value(value: object, default: bool) -> bool:
        """Return a boolean value or the provided default."""

        if value is None:
            return default
        if isinstance(value, bool):
            return value
        raise ValueError("boolean value expected")

    @staticmethod
    def first_non_empty_string(*values: object) -> str:
        """Return the first non-empty string from the provided values."""

        for value in values:
            if value is None:
                continue
            if not isinstance(value, str):
                raise ValueError("string value expected")
            if value:
                return value
        raise ValueError("string value expected")

    @staticmethod
    def list_value(value: object, name: str) -> list[object]:
        """Return a cloned list value or fail with a clear schema error."""

        if value is None:
            return []
        if isinstance(value, list):
            return deepcopy(value)
        raise ValueError(f"{name} must be a list")

    @staticmethod
    def mapping(value: object, name: str) -> dict[str, object]:
        """Return a cloned mapping value or fail with a clear schema error."""

        if value is None:
            return {}
        if isinstance(value, dict):
            return deepcopy(value)
        raise ValueError(f"{name} must be a mapping")

    @staticmethod
    def value_or_default(value: object, default: object) -> object:
        """Return a cloned explicit value or a cloned default when missing."""

        if value is None:
            return deepcopy(default)
        return deepcopy(value)

    @staticmethod
    def int_value(value: object, default: int) -> int:
        """Return a non-negative integer value or the provided default."""

        if value is None:
            return default
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("non-negative integer value expected")
        return value


class DesiredStateDefaultsSectionNormalizer:
    """Shared scaffolding for section normalizers that depend on defaults."""

    def __init__(self, resolver: DesiredStateValueResolver) -> None:
        self._resolver = resolver

    def normalize(
        self,
        config: dict[str, object],
        defaults: dict[str, object],
    ) -> dict[str, object]:
        """Return the normalized section."""

        return self._normalize(config, defaults)

    def _normalize(
        self,
        config: dict[str, object],
        defaults: dict[str, object],
    ) -> dict[str, object]:
        raise NotImplementedError()


class DesiredStateDefaultsFactory:
    """Build the default desired-state document for a selected state slug."""

    def __init__(self, state_slug: str) -> None:
        self._state_slug = state_slug

    def build(self) -> dict[str, object]:
        """Return the full default desired-state mapping."""

        return {
            "user": {
                "name": "root",
                "home": "/home/root",
                "projects_directory": "/home/root/Documents/dev-projects",
                "state_dir": f"/home/root/.local/state/{self._state_slug}",
            },
            "system": {
                "state_dir": f"/etc/{self._state_slug}",
                "locale": "en_US.UTF-8",
                "timezone": "Europe/Paris",
                "packages": {
                    "prerequisites": ["locales", "tzdata"],
                    "apt": [],
                    "cache_valid_time": 86400,
                },
                "repositories": {"apt": []},
                "directories": [],
                "services": {"enabled": [], "disabled": []},
                "settings": {"sysctl": {"fs.inotify.max_user_watches": "524288"}},
            },
            "desktop": {
                "flatpak": {
                    "enabled": True,
                    "remote": "flathub",
                    "packages": [],
                },
                "browser": {
                    "default": True,
                    "profiles": [],
                    "policies": {},
                },
                "gnome": {"dark_mode": True, "favorites": []},
            },
            "development": {
                "packages": [],
                "editor_packages": [],
                "git": {
                    "default_branch": "main",
                    "editor": "nvim",
                    "signing": {"enabled": False},
                },
                "runtimes": {},
            },
            "user_config": {
                "files": [],
                "shell": {
                    "aliases": {},
                    "environment": {},
                    "local_override_path": ".config/ubuntu-config/local.zsh",
                },
            },
            "secrets": {
                "enabled": False,
                "provider": "bitwarden",
                "bitwarden": {
                    "server": "https://vault.bitwarden.eu",
                    "ssh_keys": [],
                    "gpg_keys": [],
                    "browser_recovery_items": [],
                },
            },
        }
