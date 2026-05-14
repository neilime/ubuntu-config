"""Unit tests for managed state content helpers."""

from __future__ import annotations

import json

import pytest
from ansible_collections.neilime.ubuntu_config.plugins.module_utils.managed_state import (
    ManagedStateContentBuilder,
)


def test_build_system_content_returns_expected_json() -> None:
    """System state content should contain the fixed project and branch payload."""

    # Arrange
    builder = ManagedStateContentBuilder()
    expected_payload = {
        "project": "ubuntu-config",
        "branch": "v1",
        "managed": True,
    }

    # Act
    content = builder.build_system_content("v1")

    # Assert
    assert json.loads(content) == expected_payload
    assert content.endswith("\n")


def test_build_user_content_returns_expected_json() -> None:
    """User state content should contain the fixed project and selected user."""

    # Arrange
    builder = ManagedStateContentBuilder()
    expected_payload = {
        "project": "ubuntu-config",
        "user": "ubuntu",
        "managed": True,
    }

    # Act
    content = builder.build_user_content("ubuntu")

    # Assert
    assert json.loads(content) == expected_payload
    assert content.endswith("\n")


def test_build_system_content_rejects_empty_branch() -> None:
    """An empty branch value should be rejected before serializing state."""

    # Arrange
    builder = ManagedStateContentBuilder()
    empty_branch = ""

    # Act / Assert
    with pytest.raises(ValueError, match="must not be empty"):
        builder.build_system_content(empty_branch)


def test_build_user_content_rejects_empty_user() -> None:
    """An empty user value should be rejected before serializing state."""

    # Arrange
    builder = ManagedStateContentBuilder()
    empty_user = ""

    # Act / Assert
    with pytest.raises(ValueError, match="must not be empty"):
        builder.build_user_content(empty_user)
