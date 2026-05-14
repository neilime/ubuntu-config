"""Helpers for building ubuntu-config managed state documents."""

from __future__ import annotations

import json


class ManagedStateContentBuilder:
    """Build serialized state markers for the ubuntu-config install flow."""

    def __init__(self, project: str = "ubuntu-config") -> None:
        self._project = project

    def build_system_content(self, branch: str) -> str:
        """Return the serialized system state payload for the selected branch."""

        if not branch:
            raise ValueError("branch must not be empty")

        return self._serialize(
            {
                "project": self._project,
                "branch": branch,
                "managed": True,
            }
        )

    def build_user_content(self, user: str) -> str:
        """Return the serialized user state payload for the selected user."""

        if not user:
            raise ValueError("user must not be empty")

        return self._serialize(
            {
                "project": self._project,
                "user": user,
                "managed": True,
            }
        )

    @staticmethod
    def _serialize(payload: dict[str, object]) -> str:
        """Serialize a managed state payload with stable formatting."""

        return json.dumps(payload, indent=2) + "\n"
