import itertools
import os
import re
import sys
from collections.abc import Iterable
from typing import Optional, Union

import yaml

from chart_review import defines, errors


class ProjectConfig:
    _NUMBER_REGEX = re.compile(r"\d+")
    _RANGE_REGEX = re.compile(r"\d+-\d+")

    def __init__(self, project_dir: Optional[str] = None, config_path: Optional[str] = None):
        """
        :param project_dir: str like /opt/labelstudio/study_name
        """
        self.project_dir = project_dir or "."
        try:
            self._data = self._load_config(config_path) or {}
        except Exception as exc:
            errors.exit_for_invalid_project(str(exc))

        # ** Annotators **
        # Internally, we're often dealing with numeric ID as the primary annotator identifier,
        # since that's what is stored in Label Studio. So that's what we return from this method.
        # But as humans writing config files, it's more natural to think of "name -> id".
        # So that's what we keep in the config, and we just reverse it here for convenience.
        self.annotators = defines.AnnotatorMap()
        self.external_annotations = {}
        for name, value in self._data.get("annotators", {}).items():
            if isinstance(value, int):  # real annotation layer in Label Studio
                self.annotators[value] = name
            else:  # fake/external annotation layer that we will inject
                self.external_annotations[name] = value

        # ** Note ranges **
        # Handle some extra syntax like 1-3 == [1, 2, 3]
        self.note_ranges: dict[str, list[int]] = self._data.get("ranges", {})
        for key, values in self.note_ranges.items():
            self.note_ranges[key] = list(self._parse_note_range(values))

        # ** Implied labels **
        self.implied_labels = defines.ImpliedLabels()
        for key, value in self._data.get("implied-labels", {}).items():
            # Coerce single labels into a set
            if not isinstance(value, list):
                value = {value}
            self.implied_labels[key] = set(value)

        # ** Grouped labels **
        self.grouped_labels = defines.GroupedLabels()
        for key, value in self._data.get("grouped-labels", {}).items():
            # Coerce single labels into a set
            if not isinstance(value, list):
                value = {value}
            self.grouped_labels[key] = set(value)

    def path(self, filename: str) -> str:
        return os.path.join(self.project_dir, filename)

    @staticmethod
    def _read_yaml(path) -> dict:
        with open(path, encoding="utf8") as f:
            return yaml.safe_load(f)

    def _load_config(self, config_path: Optional[str]) -> dict:
        if config_path is None:
            # Support config.json in case folks prefer that
            try:
                config = self._read_yaml(self.path("config.json"))
            except FileNotFoundError:
                try:
                    config = self._read_yaml(self.path("config.yaml"))
                except FileNotFoundError:
                    config = {}
        else:
            # Don't resolve config_path relative to the project dir, because
            # this will have come from the command line and will resolve relative to `pwd`.
            config = self._read_yaml(config_path)

        # Do some minimal validation on the config file
        if not isinstance(config, dict):
            raise ValueError("Config file is not in the expected dictionary format.")

        return config

    def _parse_note_range(self, value: Union[str, int, list[Union[str, int]]]) -> Iterable[int]:
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
    def class_labels(self) -> defines.LabelSet:
        return set(self._data.setdefault("labels", []))

    @property
    def ignore(self) -> set[str]:
        return set(self._data.setdefault("ignore", []))
