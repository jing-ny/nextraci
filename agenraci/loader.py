"""Load a ``charter.yaml`` into a :class:`~agenraci.schema.Charter`."""

from __future__ import annotations

from pathlib import Path

import yaml

from .schema import Charter


class _StrictLoader(yaml.SafeLoader):
    """A safe YAML loader that refuses *duplicate* mapping keys.

    Plain ``yaml.safe_load`` keeps the **last** value when a key repeats, so a
    charter with two ``actions:`` blocks — or two actions of the same name —
    would quietly lose half its content. For a file that is meant to be a team's
    source of truth, a silently vanishing rule is a trust bug, so we reject it
    loudly (with a line number) instead.
    """

    def construct_mapping(self, node, deep=False):  # type: ignore[override]
        seen: set = set()
        for key_node, _value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    "while reading a charter",
                    node.start_mark,
                    f"duplicate key {key!r} — the later value would silently "
                    f"overwrite the first; remove or rename one",
                    key_node.start_mark,
                )
            seen.add(key)
        return super().construct_mapping(node, deep)


def load_charter_str(text: str) -> Charter:
    """Parse a charter from a YAML string."""
    data = yaml.load(text, Loader=_StrictLoader) or {}
    return Charter.model_validate(data)


def load_charter(path: str | Path) -> Charter:
    """Parse a charter from a YAML file path."""
    return load_charter_str(Path(path).read_text(encoding="utf-8"))
