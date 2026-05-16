"""Helpers for computing primary browser associations."""

from __future__ import annotations


# pylint: disable=too-few-public-methods
class PrimaryBrowserDefaultsPlanner:
    """Plan user-scoped browser default operations."""

    _desktop_entry = "google-chrome.desktop"

    def build_command_prefix(self, current_user: str, target_user: str) -> list[str]:
        """Return the command prefix required to run as the target user."""

        normalized_current_user = self._normalize_required_value(
            current_user, "current_user"
        )
        normalized_target_user = self._normalize_required_value(
            target_user, "target_user"
        )

        if normalized_current_user == normalized_target_user:
            return []

        return ["sudo", "-H", "-u", normalized_target_user]

    def should_apply_defaults(
        self,
        http_default: str,
        https_default: str,
        html_default: str,
        desktop_entry: str | None = None,
    ) -> bool:
        """Return whether the browser associations need to be updated."""

        normalized_desktop_entry = self._normalize_required_value(
            desktop_entry or self._desktop_entry,
            "desktop_entry",
        )

        return any(
            self._normalize_association(current_value) != normalized_desktop_entry
            for current_value in [http_default, https_default, html_default]
        )

    def _normalize_association(self, value: str) -> str:
        """Normalize a desktop association read from xdg-mime output."""

        return (value or "").strip()

    def _normalize_required_value(self, value: str, name: str) -> str:
        """Validate that required string inputs are present."""

        normalized_value = (value or "").strip()
        if not normalized_value:
            raise ValueError(f"{name} must not be empty")

        return normalized_value
