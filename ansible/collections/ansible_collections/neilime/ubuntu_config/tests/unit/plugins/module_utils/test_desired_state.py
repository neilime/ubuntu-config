"""Unit tests for desired state schema normalization."""

from __future__ import annotations

import pytest
from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state import (
    DesiredStateConfigNormalizer,
)


def test_normalize_returns_complete_shape_for_minimal_config() -> None:
    """Missing optional sections should collapse to documented defaults."""

    # Arrange
    normalizer = DesiredStateConfigNormalizer()
    raw_config: dict[str, object] = {}
    environment = {"USER": "emilien"}

    # Act
    normalized = normalizer.normalize(raw_config, environment)

    # Assert
    assert normalized["user"] == {
        "name": "emilien",
        "home": "/home/emilien",
        "projects_directory": "/home/emilien/Documents/dev-projects",
        "state_dir": "/home/emilien/.local/state/ubuntu-config-v1",
    }
    assert normalized["system"]["state_dir"] == "/etc/ubuntu-config-v1"
    assert normalized["system"]["locale"] == "en_US.UTF-8"
    assert normalized["system"]["timezone"] == "Europe/Paris"
    assert normalized["system"]["packages"]["prerequisites"] == [
        "locales",
        "tzdata",
    ]
    assert normalized["system"]["packages"]["apt"] == []
    assert normalized["system"]["packages"]["cache_valid_time"] == 86400
    assert normalized["system"]["repositories"]["apt"] == []
    assert normalized["system"]["directories"] == []
    assert normalized["system"]["services"]["enabled"] == []
    assert normalized["system"]["services"]["disabled"] == []
    assert normalized["system"]["settings"]["sysctl"] == {
        "fs.inotify.max_user_watches": "524288"
    }
    assert normalized["desktop"]["flatpak"]["enabled"] is True
    assert normalized["desktop"]["flatpak"]["remote"] == "flathub"
    assert normalized["desktop"]["browser"]["default"] is True
    assert normalized["desktop"]["browser"]["profiles"] == []
    assert normalized["development"]["git"]["default_branch"] == "main"
    assert normalized["development"]["git"]["editor"] == "nvim"
    assert normalized["development"]["git"]["signing"]["enabled"] is False
    assert (
        normalized["user_config"]["shell"]["local_override_path"]
        == ".config/ubuntu-config/local.zsh"
    )
    assert normalized["secrets"]["enabled"] is False
    assert normalized["secrets"]["provider"] == "bitwarden"
    assert normalized["secrets"]["bitwarden"]["server"] == "https://vault.bitwarden.eu"
    assert normalized["secrets"]["bitwarden"]["ssh_keys"] == []
    assert normalized["secrets"]["bitwarden"]["gpg_keys"] == []
    assert normalized["secrets"]["bitwarden"]["browser_recovery_items"] == []


def test_normalize_preserves_declared_values_and_env_overrides() -> None:
    """Declared values should survive normalization unless env overrides apply."""

    # Arrange
    normalizer = DesiredStateConfigNormalizer()
    github_cli_source = (
        "deb [signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] "
        "https://cli.github.com/packages stable main"
    )
    github_cli_repository = {
        "name": "github-cli",
        "source": github_cli_source,
        "keyring": {
            "url": "https://cli.github.com/packages/githubcli-archive-keyring.gpg",
            "path": "/usr/share/keyrings/githubcli-archive-keyring.gpg",
        },
    }
    raw_config = {
        "user": {
            "name": "declared",
            "home": "/srv/declared",
            "projects_directory": "/workspace/projects",
            "state_dir": "/workspace/state",
        },
        "system": {
            "state_dir": "/var/lib/ubuntu-config",
            "locale": "fr_FR.UTF-8",
            "timezone": "UTC",
            "packages": {
                "prerequisites": ["locales", "curl"],
                "apt": ["git"],
                "cache_valid_time": 3600,
            },
            "repositories": {"apt": [github_cli_repository]},
            "directories": [{"path": "/var/lib/ubuntu-config/cache", "mode": "0750"}],
            "services": {
                "enabled": ["systemd-timesyncd"],
                "disabled": ["apache2"],
            },
            "settings": {"sysctl": {"fs.inotify.max_user_watches": "524288"}},
        },
        "desktop": {
            "flatpak": {
                "enabled": False,
                "remote": "custom",
                "packages": ["com.brave.Browser"],
            },
            "browser": {
                "default": False,
                "profiles": [{"id": "personal"}],
                "policies": {"PasswordManagerEnabled": False},
            },
            "gnome": {
                "dark_mode": False,
                "favorites": ["org.gnome.Terminal.desktop"],
            },
        },
        "development": {
            "packages": ["git"],
            "editor_packages": ["com.visualstudio.code"],
            "git": {
                "default_branch": "trunk",
                "editor": "vim",
                "signing": {"enabled": True},
            },
            "runtimes": {"node": {"manager": "fnm"}},
        },
        "user_config": {
            "files": [{"path": ".gitconfig"}],
            "shell": {
                "aliases": {"ll": "ls -alF"},
                "environment": {"EDITOR": "nvim"},
                "local_override_path": ".config/ubuntu-config/private.zsh",
            },
        },
        "secrets": {
            "enabled": True,
            "provider": "bitwarden",
            "bitwarden": {
                "server": "https://vault.example.test",
                "ssh_keys": [{"id": "main"}],
                "gpg_keys": [{"id": "default"}],
                "browser_recovery_items": [{"profile": "personal"}],
            },
        },
    }
    environment = {
        "UBUNTU_CONFIG_USER": "override",
        "UBUNTU_CONFIG_USER_HOME": "/home/override",
        "UBUNTU_CONFIG_USER_STATE_DIR": "/state/override",
        "UBUNTU_CONFIG_SYSTEM_STATE_DIR": "/system/override",
    }

    # Act
    normalized = normalizer.normalize(raw_config, environment)

    # Assert
    assert normalized["user"] == {
        "name": "override",
        "home": "/home/override",
        "projects_directory": "/workspace/projects",
        "state_dir": "/state/override",
    }
    assert normalized["system"]["state_dir"] == "/system/override"
    assert normalized["system"]["locale"] == "fr_FR.UTF-8"
    assert normalized["system"]["timezone"] == "UTC"
    assert normalized["system"]["packages"]["prerequisites"] == ["locales", "curl"]
    assert normalized["system"]["packages"]["apt"] == ["git"]
    assert normalized["system"]["packages"]["cache_valid_time"] == 3600
    assert normalized["system"]["repositories"]["apt"] == [github_cli_repository]
    assert normalized["system"]["directories"] == [
        {"path": "/var/lib/ubuntu-config/cache", "mode": "0750"}
    ]
    assert normalized["system"]["services"]["enabled"] == ["systemd-timesyncd"]
    assert normalized["system"]["services"]["disabled"] == ["apache2"]
    assert normalized["system"]["settings"]["sysctl"] == {
        "fs.inotify.max_user_watches": "524288"
    }
    assert normalized["desktop"]["flatpak"]["enabled"] is False
    assert normalized["desktop"]["flatpak"]["remote"] == "custom"
    assert normalized["desktop"]["flatpak"]["packages"] == ["com.brave.Browser"]
    assert normalized["desktop"]["browser"]["default"] is False
    assert normalized["desktop"]["browser"]["profiles"] == [{"id": "personal"}]
    assert normalized["desktop"]["browser"]["policies"] == {
        "PasswordManagerEnabled": False
    }
    assert normalized["desktop"]["gnome"]["dark_mode"] is False
    assert normalized["desktop"]["gnome"]["favorites"] == ["org.gnome.Terminal.desktop"]
    assert normalized["development"]["packages"] == ["git"]
    assert normalized["development"]["editor_packages"] == ["com.visualstudio.code"]
    assert normalized["development"]["git"]["default_branch"] == "trunk"
    assert normalized["development"]["git"]["editor"] == "vim"
    assert normalized["development"]["git"]["signing"]["enabled"] is True
    assert normalized["development"]["runtimes"] == {"node": {"manager": "fnm"}}
    assert normalized["user_config"]["files"] == [{"path": ".gitconfig"}]
    assert normalized["user_config"]["shell"]["aliases"] == {"ll": "ls -alF"}
    assert normalized["user_config"]["shell"]["environment"] == {"EDITOR": "nvim"}
    assert (
        normalized["user_config"]["shell"]["local_override_path"]
        == ".config/ubuntu-config/private.zsh"
    )
    assert normalized["secrets"]["enabled"] is True
    assert normalized["secrets"]["provider"] == "bitwarden"
    assert normalized["secrets"]["bitwarden"]["server"] == "https://vault.example.test"
    assert normalized["secrets"]["bitwarden"]["ssh_keys"] == [{"id": "main"}]
    assert normalized["secrets"]["bitwarden"]["gpg_keys"] == [{"id": "default"}]
    assert normalized["secrets"]["bitwarden"]["browser_recovery_items"] == [
        {"profile": "personal"}
    ]


def test_normalize_rejects_invalid_section_types() -> None:
    """Wrong section types should fail with a clear validation error."""

    # Arrange
    normalizer = DesiredStateConfigNormalizer()
    invalid_config: dict[str, object] = {"desktop": []}
    environment = {"USER": "emilien"}

    # Act / Assert
    with pytest.raises(ValueError, match="ubuntu_config.desktop must be a mapping"):
        normalizer.normalize(invalid_config, environment)


def test_normalize_preserves_explicit_empty_system_lists() -> None:
    """Explicit empty system lists should not fall back to non-empty defaults."""

    # Arrange
    normalizer = DesiredStateConfigNormalizer()
    raw_config = {
        "system": {
            "packages": {"prerequisites": [], "apt": []},
            "directories": [],
            "services": {"enabled": [], "disabled": []},
            "settings": {"sysctl": {}},
        }
    }
    environment = {"USER": "emilien"}

    # Act
    normalized = normalizer.normalize(raw_config, environment)

    # Assert
    assert normalized["system"]["packages"]["prerequisites"] == []
    assert normalized["system"]["packages"]["apt"] == []
    assert normalized["system"]["directories"] == []
    assert normalized["system"]["services"]["enabled"] == []
    assert normalized["system"]["services"]["disabled"] == []
    assert normalized["system"]["settings"]["sysctl"] == {}


def test_normalize_rejects_invalid_package_cache_policy() -> None:
    """Non-integer package cache policies should fail with a clear error."""

    # Arrange
    normalizer = DesiredStateConfigNormalizer()
    raw_config = {"system": {"packages": {"cache_valid_time": "daily"}}}
    environment = {"USER": "emilien"}

    # Act / Assert
    with pytest.raises(ValueError, match="non-negative integer value expected"):
        normalizer.normalize(raw_config, environment)
