"""Filter plugins for normalizing the desired ubuntu-config schema."""

from __future__ import annotations

from ansible_collections.neilime.ubuntu_config.plugins.module_utils.desired_state import (
    DesiredStateConfigNormalizer,
)

_normalizer = DesiredStateConfigNormalizer()


# pylint: disable=too-few-public-methods
class FilterModule:
    """Expose desired state helpers as Ansible filters."""

    def filters(self) -> dict[str, object]:
        """Return the filters provided by this collection."""

        return {
            "normalized_ubuntu_config": _normalizer.normalize,
        }
