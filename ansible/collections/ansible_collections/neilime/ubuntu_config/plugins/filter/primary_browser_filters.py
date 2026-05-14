"""Filter plugins for primary browser planning helpers."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.primary_browser import (
    PrimaryBrowserDefaultsPlanner,
)

_planner = PrimaryBrowserDefaultsPlanner()


# pylint: disable=too-few-public-methods
class FilterModule:
    """Expose primary browser helpers as Ansible filters."""

    def filters(self) -> dict[str, object]:
        """Return the filters provided by this collection."""

        return {
            "primary_browser_command_prefix": _planner.build_command_prefix,
            "primary_browser_should_apply_defaults": _planner.should_apply_defaults,
        }
