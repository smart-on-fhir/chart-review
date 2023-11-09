import os
from collections.abc import Iterable
from chart_review.common import guard_str, guard_iter, guard_in
from chart_review import common
from chart_review import config
from chart_review import external
from chart_review import simplify
from chart_review import mentions
from chart_review import agree


class CohortReader:
    def __init__(self, project_dir: str):
        """
        :param project_dir: str like /opt/labelstudio/study_name
        """
        self.project_dir = project_dir
        self.config = config.ProjectConfig(project_dir)
        self.labelstudio_json = self.path(
            "labelstudio-export.json"
        )  # TODO: refactor labelstudio.py
        self.annotator = self.config.annotators
        self.note_range = self.config.note_ranges
        self.class_labels = self.config.class_labels
        self.annotations = None

        saved = common.read_json(self.labelstudio_json)
        if isinstance(saved, list):
            self.annotations = simplify.simplify_full(self.labelstudio_json, self.annotator)
        else:
            # TODO: int keys cant be saved in JSON, compatability hack use instead LabelStudio.py
            compat = dict()
            compat["files"] = saved["files"]
            compat["annotations"] = dict()
            for k in saved["annotations"].keys():
                compat["annotations"][int(k)] = saved["annotations"][k]
            self.annotations = compat

        # Load external annotations (i.e. from NLP tags or ICD10 codes)
        for name, value in self.config.external_annotations.items():
            self.annotations = external.merge_external(
                self.annotations, saved, project_dir, name, value
            )

        # Detect note ranges if they were not defined in the project config
        # (i.e. default to the full set of annotated notes)
        all_names = list(self.annotator.values())
        all_names += list(self.config.external_annotations.keys())
        for annotator in all_names:
            if annotator not in self.note_range:
                notes = []
                for note_id, annotations in self.annotations["annotations"].items():
                    if annotator in annotations:
                        notes.append(note_id)
                self.note_range[annotator] = notes

    def path(self, filename):
        return os.path.join(self.project_dir, filename)

    def calc_term_freq(self, annotator) -> dict:
        """
        Calculate Term Frequency of highlighted mentions.
        :param annotator: an annotator name
        :return: dict key=TERM val= {label, list of chart_id}
        """
        return mentions.calc_term_freq(self.annotations, guard_str(annotator))

    def calc_label_freq(self, annotator) -> dict:
        """
        Calculate Term Frequency of highlighted mentions.
        :param annotator: an annotator name
        :return: dict key=TERM val= {label, list of chart_id}
        """
        return mentions.calc_label_freq(self.calc_term_freq(annotator))

    def calc_term_label_confusion(self, annotator) -> dict:
        return mentions.calc_term_label_confusion(self.calc_term_freq(annotator))

    def confusion_matrix(
        self, truth: str, annotator: str, note_range: Iterable, label_pick=None
    ) -> dict:
        """
        This is the rollup of counting each symptom only once, not multiple times.

        :param truth: annotator to use as the ground truth
        :param annotator: another annotator to compare with truth
        :param note_range: collection of LabelStudio document ID
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict
        """
        return agree.confusion_matrix(self.annotations, truth, annotator, note_range, label_pick)

    def score_reviewer(self, truth: str, annotator: str, note_range, label_pick=None):
        """
        Score reliability of rater at the level of all symptom *PREVALENCE*
        :param truth: annotator to use as the ground truth
        :param annotator: another annotator to compare with truth
        :param note_range: default= all in corpus
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict, keys f1, precision, recall and vals= %score
        """
        if label_pick:
            guard_in(label_pick, self.class_labels)

        return agree.score_reviewer(
            self.annotations, truth, annotator, guard_iter(note_range), label_pick
        )

    def score_reviewer_table_csv(self, truth: str, annotator: str, note_range) -> str:
        table = list()
        table.append(agree.csv_header(False, True))

        score = self.score_reviewer(truth, annotator, note_range)
        table.append(agree.csv_row_score(score))

        for label in self.class_labels:
            score = self.score_reviewer(truth, annotator, note_range, label)
            table.append(agree.csv_row_score(score, label))

        return "\n".join(table) + "\n"

    def score_reviewer_table_dict(self, truth, annotator, note_range) -> dict:
        table = self.score_reviewer(truth, annotator, note_range)

        for label in self.class_labels:
            table[label] = self.score_reviewer(truth, annotator, note_range, label)

        return table
