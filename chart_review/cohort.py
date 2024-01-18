from typing import Iterable, Optional

from chart_review.common import guard_str, guard_iter, guard_in
from chart_review import agree
from chart_review import common
from chart_review import config
from chart_review import external
from chart_review import term_freq
from chart_review import simplify
from chart_review import types


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
        saved = common.read_json(self.config.path("labelstudio-export.json"))
        self.annotations = simplify.simplify_export(saved, self.config)

        # Load external annotations (i.e. from NLP tags or ICD10 codes)
        for name, value in self.config.external_annotations.items():
            external.merge_external(self.annotations, saved, self.project_dir, name, value)

        # Parse ignored IDs (might be note IDs, might be external IDs)
        self.ignored_notes: set[int] = set()
        for ignore_id in self.config.ignore:
            ls_id = external.external_id_to_label_studio_id(saved, str(ignore_id))
            if ls_id is None:
                if isinstance(ignore_id, int):
                    ls_id = ignore_id  # must be direct note ID
                else:
                    # Must just be over-zealous excluding (like automatically from SQL)
                    continue
            self.ignored_notes.add(ls_id)

        # Consolidate/expand mentions based on config
        simplify.simplify_mentions(
            self.annotations,
            implied_labels=self.config.implied_labels,
            grouped_labels=self.config.grouped_labels,
        )

        # Detect note ranges if they were not defined in the project config
        # (i.e. default to the full set of annotated notes)
        self.note_range = self.config.note_ranges
        for annotator, annotator_mentions in self.annotations.mentions.items():
            if annotator not in self.note_range:
                self.note_range[annotator] = sorted(annotator_mentions.keys())

    @property
    def class_labels(self):
        return self.annotations.labels

    def calc_term_freq(self, annotator) -> dict:
        """
        Calculate Term Frequency of highlighted mentions.
        :param annotator: an annotator name
        :return: dict key=TERM val= {label, list of chart_id}
        """
        return term_freq.calc_term_freq(self.annotations, guard_str(annotator))

    def calc_label_freq(self, annotator) -> dict:
        """
        Calculate Term Frequency of highlighted mentions.
        :param annotator: an annotator name
        :return: dict key=TERM val= {label, list of chart_id}
        """
        return term_freq.calc_label_freq(self.calc_term_freq(annotator))

    def calc_term_label_confusion(self, annotator) -> dict:
        return term_freq.calc_term_label_confusion(self.calc_term_freq(annotator))

    def _select_labels(self, label_pick: str = None) -> Optional[Iterable[str]]:
        if label_pick:
            guard_in(label_pick, self.class_labels)
            return [label_pick]
        elif self.class_labels:
            return self.class_labels
        else:
            return None

    def confusion_matrix(
        self, truth: str, annotator: str, note_range: Iterable, label_pick: str = None
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
        note_range = set(guard_iter(note_range)) - self.ignored_notes
        return agree.confusion_matrix(
            self.annotations,
            truth,
            annotator,
            note_range,
            labels=labels,
        )

    def score_reviewer(self, truth: str, annotator: str, note_range, label_pick: str = None):
        """
        Score reliability of rater at the level of all symptom *PREVALENCE*
        :param truth: annotator to use as the ground truth
        :param annotator: another annotator to compare with truth
        :param note_range: default= all in corpus
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict, keys f1, precision, recall and vals= %score
        """
        labels = self._select_labels(label_pick)
        note_range = set(guard_iter(note_range)) - self.ignored_notes
        return agree.score_reviewer(self.annotations, truth, annotator, note_range, labels=labels)

    def score_reviewer_table_csv(self, truth: str, annotator: str, note_range) -> str:
        table = list()
        table.append(agree.csv_header(False, True))

        score = self.score_reviewer(truth, annotator, note_range)
        table.append(agree.csv_row_score(score, as_string=True))

        for label in self.class_labels:
            score = self.score_reviewer(truth, annotator, note_range, label)
            table.append(agree.csv_row_score(score, label, as_string=True))

        return "\n".join(table) + "\n"

    def score_reviewer_table_dict(self, truth, annotator, note_range) -> dict:
        table = self.score_reviewer(truth, annotator, note_range)

        for label in self.class_labels:
            table[label] = self.score_reviewer(truth, annotator, note_range, label)

        return table
