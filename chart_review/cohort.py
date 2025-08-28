from collections.abc import Iterable
from typing import Optional

from chart_review import agree, common, config, defines, errors, external, simplify


class CohortReader:
    """
    CohortReader converts a Label Studio export and a project config into a standard form.

    It also exposes some statistical helper methods.
    """

    def __init__(self, proj_config: config.ProjectConfig):
        """
        :param proj_config: parsed project configuration
        """
        self.config = proj_config
        self.project_dir = self.config.project_dir

        # Load exported annotations
        try:
            self.ls_export = common.read_json(self.config.path("labelstudio-export.json"))
        except Exception as exc:
            errors.exit_for_invalid_project(str(exc))

        self.annotations = simplify.simplify_export(self.ls_export, self.config)

        # Add a placeholder for any annotators that don't have mentions for some reason
        for annotator in self.config.annotators.values():
            self.annotations.mentions.setdefault(annotator, defines.Mentions())

        # Load external annotations (i.e. from NLP tags or ICD10 codes)
        for name, value in self.config.external_annotations.items():
            external.merge_external(self.annotations, self.ls_export, self.project_dir, name, value)

        # Consolidate/expand mentions based on config
        simplify.simplify_mentions(
            self.annotations,
            implied_labels=self.config.implied_labels,
            grouped_labels=self.config.grouped_labels,
        )

        # Calculate the final set of note ranges for each annotator
        self.note_range, self.ignored_notes = self._collect_note_ranges(self.ls_export)

        # Remove any ignored notes from the annotations, for ease of consuming code
        for note in self.ignored_notes:
            self.annotations.remove(note)

    def _collect_note_ranges(
        self, exported_json: list[dict]
    ) -> tuple[dict[str, defines.NoteSet], defines.NoteSet]:
        # Detect note ranges if they were not defined in the project config
        # (i.e. default to the full set of annotated notes)
        note_ranges = {k: set(v) for k, v in self.config.note_ranges.items()}
        for annotator, annotator_mentions in self.annotations.mentions.items():
            if annotator not in note_ranges:
                note_ranges[annotator] = set(annotator_mentions.keys())

        all_ls_notes = {int(entry["id"]) for entry in exported_json if "id" in entry}

        # Parse ignored IDs (might be note IDs, might be external IDs)
        ignored_notes = defines.NoteSet()
        for ignore_id in self.config.ignore:
            ls_id = external.external_id_to_label_studio_id(exported_json, str(ignore_id))
            if ls_id is None:
                if isinstance(ignore_id, int):
                    ls_id = ignore_id  # must be direct note ID
                else:
                    # Must just be over-zealous excluding (like automatically from SQL)
                    continue  # pragma: no cover
            if ls_id in all_ls_notes:
                ignored_notes.add(ls_id)

        # Remove any invalid (ignored, non-existent) notes from the range sets
        for note_ids in note_ranges.values():
            note_ids.difference_update(ignored_notes)
            note_ids.intersection_update(all_ls_notes)

        return note_ranges, ignored_notes

    @property
    def class_labels(self):
        return self.annotations.labels

    def _select_labels(self, label_pick: Optional[str] = None) -> Iterable[str]:
        if label_pick:
            return [label_pick]
        else:
            return self.class_labels

    def confusion_matrix(
        self,
        truth: str,
        annotator: str,
        note_range: defines.NoteSet,
        label_pick: Optional[str] = None,
    ) -> dict:
        """
        This is the rollup of counting each symptom only once, not multiple times.

        :param truth: annotator to use as the ground truth
        :param annotator: another annotator to compare with truth
        :param note_range: collection of LabelStudio document ID
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict
        """
        labels = self._select_labels(label_pick)
        return agree.confusion_matrix(
            self.annotations,
            truth,
            annotator,
            note_range,
            labels=labels,
        )

    def contingency_table(
        self,
        truth: str,
        annotator1: str,
        annotator2: str,
        note_range: defines.NoteSet,
        label_pick: Optional[str] = None,
    ) -> dict:
        """
        Calculate a contingency table for truth and two annotators.

        https://en.wikipedia.org/wiki/Contingency_table

        :param truth: annotator to use as the ground truth
        :param annotator1: one annotator to compare
        :param annotator2: another annotator to compare
        :param note_range: collection of LabelStudio document ID
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict
        """
        labels = self._select_labels(label_pick)
        return agree.contingency_table(
            self.annotations,
            truth,
            annotator1,
            annotator2,
            note_range,
            labels=labels,
        )
