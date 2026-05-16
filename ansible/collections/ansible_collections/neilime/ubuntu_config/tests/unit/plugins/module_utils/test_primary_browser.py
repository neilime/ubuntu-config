"""Unit tests for primary browser helpers."""

from __future__ import annotations

import pytest
from ansible_collections.neilime.ubuntu_config.plugins.module_utils.primary_browser import (
    PrimaryBrowserDefaultsPlanner,
)


def test_build_command_prefix_returns_empty_list_for_target_user() -> None:
    """Running as the target user should not require sudo."""

    # Arrange
    planner = PrimaryBrowserDefaultsPlanner()

    # Act
    command_prefix = planner.build_command_prefix("emilien", "emilien")

    # Assert
    assert command_prefix == []


def test_build_command_prefix_returns_sudo_prefix_for_other_user() -> None:
    """Running as another user should switch identity explicitly."""

    # Arrange
    planner = PrimaryBrowserDefaultsPlanner()

    # Act
    command_prefix = planner.build_command_prefix("root", "emilien")

    # Assert
    assert command_prefix == ["sudo", "-H", "-u", "emilien"]


def test_build_command_prefix_rejects_empty_target_user() -> None:
    """An empty target user should fail before building a command."""

    # Arrange
    planner = PrimaryBrowserDefaultsPlanner()

    # Act / Assert
    with pytest.raises(ValueError, match="target_user must not be empty"):
        planner.build_command_prefix("root", "")


def test_should_apply_defaults_returns_false_when_associations_match() -> None:
    """Matching associations should keep the task idempotent."""

    # Arrange
    planner = PrimaryBrowserDefaultsPlanner()

    # Act
    should_apply = planner.should_apply_defaults(
        "google-chrome.desktop\n",
        "google-chrome.desktop",
        " google-chrome.desktop ",
    )

    # Assert
    assert should_apply is False


def test_should_apply_defaults_returns_true_when_any_association_differs() -> None:
    """Any mismatch should trigger the browser association update."""

    # Arrange
    planner = PrimaryBrowserDefaultsPlanner()

    # Act
    should_apply = planner.should_apply_defaults(
        "firefox.desktop",
        "google-chrome.desktop",
        "google-chrome.desktop",
    )

    # Assert
    assert should_apply is True


def test_should_apply_defaults_returns_true_when_association_is_missing() -> None:
    """Missing associations should be repaired by the role."""

    # Arrange
    planner = PrimaryBrowserDefaultsPlanner()

    # Act
    should_apply = planner.should_apply_defaults(
        "",
        "google-chrome.desktop",
        "google-chrome.desktop",
    )

    # Assert
    assert should_apply is True
