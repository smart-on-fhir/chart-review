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
        self.labelstudio_json = self.path('labelstudio-export.json') #TODO: refactor labelstudio.py
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
            compat['files'] = saved['files']
            compat['annotations'] = dict()
            for k in saved['annotations'].keys():
                compat['annotations'][int(k)] = saved['annotations'][k]
            self.annotations = compat

        # Load external annotations (i.e. from NLP tags or ICD10 codes)
        for name, value in self.config.external_annotations.items():
            self.annotations = external.merge_external(self.annotations, saved, project_dir, name, value)

    def path(self, filename):
        return os.path.join(self.project_dir, filename)

    def calc_term_freq(self, annotator) -> dict:
        """
        Calculate Term Frequency of highlighted mentions.
        @param annotator: Reviewer like andy, amy, or alon
        @return: dict key=TERM val= {label, list of chart_id}
        """
        return mentions.calc_term_freq(self.annotations, guard_str(annotator))

    def calc_label_freq(self, annotator) -> dict:
        """
        Calculate Term Frequency of highlighted mentions.
        :param annotator: Reviewer like andy, amy, or alon
        :return: dict key=TERM val= {label, list of chart_id}
        """
        return mentions.calc_label_freq(self.calc_term_freq(annotator))

    def calc_term_label_confusion(self, annotator) -> dict:
        return mentions.calc_term_label_confusion(self.calc_term_freq(annotator))

    def confusion_matrix(self, gold_ann, review_ann, note_range: Iterable, label_pick=None) -> dict:
        """
        This is the rollup of counting each symptom only 1x, not multiple times for a single patient.
        :param simple: prepared map of files and annotations
        :param gold_ann: annotator like andy, amy, or alon
        :param review_ann: annotator like andy, amy, or alon (usually alon)
        :param note_range: collection of LabelStudio document ID
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict
        """
        return agree.confusion_matrix(self.annotations,
                                      guard_str(gold_ann),
                                      guard_str(review_ann),
                                      note_range,
                                      label_pick)

    def score_reviewer(self, gold_ann, review_ann, note_range, label_pick=None):
        """
        Score reliability of rater at the level of all symptom *PREVALENCE*
        :param gold_ann: annotator like andy, amy, or alon
        :param review_ann: annotator like andy, amy, or alon (usually alon)
        :param note_range: default= all in corpus
        :param label_pick: (optional) of the CLASS_LABEL to score separately
        :return: dict, keys f1, precision, recall and vals= %score
        """
        if label_pick:
            guard_in(label_pick, self.class_labels)

        return agree.score_reviewer(self.annotations,
                                    guard_str(gold_ann),
                                    guard_str(review_ann),
                                    guard_iter(note_range),
                                    label_pick)

    def score_reviewer_table_csv(self, gold_ann, review_ann, note_range) -> str:
        table = list()
        table.append(agree.csv_header(False, True))

        score = self.score_reviewer(gold_ann, review_ann, note_range)
        table.append(agree.csv_row_score(score))

        for label in self.class_labels:
            score = self.score_reviewer(gold_ann, review_ann, note_range, label)
            table.append(agree.csv_row_score(score, label))

        return '\n'.join(table) + '\n'

    def score_reviewer_table_dict(self, gold_ann, review_ann, note_range) -> dict:
        table = self.score_reviewer(gold_ann, review_ann, note_range)

        for label in self.class_labels:
            table[label] = self.score_reviewer(gold_ann, review_ann, note_range, label)

        return table
