from typing import List
from collections.abc import Iterable
from enum import Enum, EnumMeta
from chartreview.common import guard_str, guard_iter, guard_in
from chartreview import common
from chartreview import simplify
from chartreview import mentions
from chartreview import agree

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
