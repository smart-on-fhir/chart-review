import itertools
import os
import re
import sys
from typing import Iterable

import yaml

AnnotatorMap = dict[int, str]


class ProjectConfig:
    _NUMBER_REGEX = re.compile(r"\d+")
    _RANGE_REGEX = re.compile(r"\d+-\d+")

    def __init__(self, project_dir: str):
        """
        :param project_dir: str like /opt/labelstudio/study_name
        """
        self._data = None

        for filename in ("config.yaml", "config.json"):
            try:
                path = os.path.join(project_dir, filename)
                with open(path, "r", encoding="utf8") as f:
                    self._data = yaml.safe_load(f)
            except FileNotFoundError:
                continue

        if self._data is None:
            raise FileNotFoundError(f"No config.yaml or config.json file found in {project_dir}")

        ### Annotators
        # Internally, we're often dealing with numeric ID as the primary annotator identifier, since that's what
        # is stored in Label Studio. So that's what we return from this method.
        # But as humans writing config files, it's more natural to think of "name -> id".
        # So that's what we keep in the config, and we just reverse it here for convenience.
        self.annotators: dict[int, str] = {}
        self.external_annotations = {}
        for name, value in self._data.get("annotators", {}).items():
            if isinstance(value, int):  # real annotation layer in Label Studio
                self.annotators[value] = name
            else:  # fake/external annotation layer that we will inject
                self.external_annotations[name] = value

        ### Note ranges
        # Handle some extra syntax like 1-3 == [1, 2, 3]
        self.note_ranges = self._data.get("ranges", {})
        for key, values in self.note_ranges.items():
            self.note_ranges[key] = list(self._parse_note_range(values))

    def _parse_note_range(self, value: str | int | list[str | int]) -> Iterable[int]:
        if isinstance(value, list):
            return list(itertools.chain.from_iterable(self._parse_note_range(v) for v in value))
        elif isinstance(value, int):
            return [value]
        elif self._NUMBER_REGEX.fullmatch(value):
            return [int(value)]
        elif self._RANGE_REGEX.fullmatch(value):
            edges = value.split("-")
            return range(int(edges[0]), int(edges[1]) + 1)
        elif value in self.note_ranges:
            return self._parse_note_range(
                self.note_ranges[value]
            )  # warning: no guards against infinite recursion
        else:
            print(f"Unknown note range '{value}'", file=sys.stderr)
            return []

    @property
    def class_labels(self) -> list[str]:
        return self._data.setdefault("labels", [])
