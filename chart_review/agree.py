from typing import Dict, List
from collections.abc import Iterable
from ctakesclient.typesystem import Span
from chart_review import mentions
from chart_review import simplify


def confusion_matrix(
    simple: dict, truth: str, annotator: str, note_range: Iterable, label_pick=None
) -> Dict[str, list]:
    """
    Confusion Matrix (TP, FP, TN, FN)
    https://www.researchgate.net/figure/Calculation-of-sensitivity-specificity-and-positive-and-negative-predictive_fig1_49650721

    This is the rollup of counting each symptom only once, not multiple times for a single patient.
    :param simple: prepared map of files and annotations
    :param truth: annotator to use as the ground truth
    :param annotator: another annotator to compare with truth
    :param note_range: collection of LabelStudio document ID
    :param label_pick: (optional) of the CLASS_LABEL to score separately
    :return: Dict
        "TP": True Positives (agree on positive+ symptom)
        "FP": False Positives (annotator said positive+, truth said No)
        "FN": False Negative (truth said positive+, annotator said No)
        "TN": True Negative (truth and annotator both said No)
    """
    truth_mentions = simplify.rollup_mentions(simple, truth, note_range)
    annotator_mentions = simplify.rollup_mentions(simple, annotator, note_range)

    # Only examine labels that were used by any compared annotators at least once
    label_set = set()
    for _v in truth_mentions.values():
        label_set |= set(_v)
    for _v in annotator_mentions.values():
        label_set |= set(_v)

    TP = list()  # True Positive
    FP = list()  # False Positive
    FN = list()  # False Negative
    TN = list()  # True Negative

    for note_id in note_range:
        for label in label_set:
            if not label_pick or (label == label_pick):  # Pick label (default=None)
                key = {note_id: label}
                truth_positive = label in truth_mentions.get(note_id, [])
                annotator_positive = label in annotator_mentions.get(note_id, [])

                if truth_positive and annotator_positive:
                    TP.append(key)
                elif truth_positive and not annotator_positive:
                    FN.append(key)
                elif not truth_positive and annotator_positive:
                    FP.append(key)
                elif not truth_positive and not annotator_positive:
                    TN.append(key)
                else:
                    raise Exception("Guard: Impossible comparison of reviewers")

    return {"TP": TP, "FN": FN, "FP": FP, "TN": TN}


def append_matrix(first: dict, second: dict) -> dict:
    """
    Append two different confusion_matrix matrix dictionaries.

    For example, (Annotator1 VS NLP) appended to (Annotator2 vs NLP).

    TODO: Warning: assumes first and second have no overlapping NoteRange,
          may not be applicable for other studies.

    :param first: confusion_matrix matrix
    :param second: confusion_matrix matrix
    :return:
    """
    added = {}
    for header in ["TP", "FP", "FN", "TN"]:
        added[header] = first[header] + second[header]
    return added


def score_matrix(matrix: dict, sig_digits=3) -> dict:
    """
    Score F1 measure with precision (PPV) and recall (sensitivity).
    F1 deliberately ignores "True Negatives" because TN inflates scoring (AUROC)
    @return: dict with keys {'f1', 'precision', 'recall'} vals are %score
    """
    true_pos = matrix["TP"]
    true_neg = matrix["TN"]
    false_pos = matrix["FP"]
    false_neg = matrix["FN"]

    if 0 == len(true_pos) or 0 == len(true_neg):
        sens = 0
        spec = 0
        ppv = 0
        npv = 0
        f1 = 0
    else:
        sens = len(true_pos) / (len(true_pos) + len(false_neg))
        spec = len(true_neg) / (len(true_neg) + len(false_pos))
        ppv = len(true_pos) / (len(true_pos) + len(false_pos))
        npv = len(true_neg) / (len(true_neg) + len(false_neg))
        f1 = (2 * ppv * sens) / (ppv + sens)

    return {
        "F1": round(f1, sig_digits),
        "Sens": round(sens, sig_digits),
        "Spec": round(spec, sig_digits),
        "PPV": round(ppv, sig_digits),
        "NPV": round(npv, sig_digits),
        "TP": len(true_pos),
        "FP": len(false_pos),
        "FN": len(false_neg),
        "TN": len(true_neg),
    }


def avg_scores(first: dict, second: dict, sig_digits=3) -> dict:
    merged = {}
    for header in csv_header():
        added = first[header] + second[header]
        if header in ["TP", "FP", "FN", "TN"]:
            merged[header] = added
        else:
            merged[header] = round(added / 2, sig_digits)
    return merged


def score_reviewer(
    simple: dict, truth: str, annotator: str, note_range: Iterable, pick_label=None
) -> dict:
    """
    Score reliability of an annotator against a truth annotator.

    :param simple: prepared map of files and annotations
    :param truth: annotator to use as the ground truth
    :param annotator: another annotator to compare with truth
    :param note_range: collection of LabelStudio document ID
    :param pick_label: (optional) of the CLASS_LABEL to score separately
    :return: dict, keys f1, precision, recall and vals= %score
    """
    truth_matrix = confusion_matrix(simple, truth, annotator, note_range, pick_label)
    return score_matrix(truth_matrix)


def csv_table(score: dict, class_labels: Iterable):
    table = list()
    table.append(csv_header(False, True))
    table.append(csv_row_score(score))

    for label in class_labels:
        table.append(csv_row_score(score[label], label))
    return "\n".join(table) + "\n"


def csv_header(pick_label=False, as_string=False):
    """
    Table Header
    F1, PPV (precision), Recall (sensitivity), True Pos, False Pos, False Neg
    :param pick_label: default= None
    :return: header
    """
    as_list = ["F1", "Sens", "Spec", "PPV", "NPV", "TP", "FN", "TN", "FP"]

    if not as_string:
        return as_list

    header = as_list
    header.append(pick_label if pick_label else "Label")
    return "\t".join(header)


def csv_row_score(score: dict, pick_label=None) -> str:
    """
    Table Row entry
    F1, PPV (precision), Recall (sensitivity), True Pos, False Pos, False Neg
    :param score: dict result from F1 scoring
    :param pick_label: default= None means '*' all classes
    :return: str representation of the score
    """
    row = [score[header] for header in csv_header()]
    row = [str(value) for value in row]
    row.append(pick_label if pick_label else "*")
    return "\t".join(row)


def true_prevalence(prevalence_apparent: float, sensitivity: float, specificity: float):
    """
    See paper: "The apparent prevalence, the true prevalence"
    https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9195606

    Using Eq. 4. it can be calculated:
    True prevalence = (Apparent prevalence + Sp - 1)/(Se + Sp - 1)

    :param prevalence_apparent: estimated prevalence, concretely:
        the %NLP labled positives / cohort

    :param: sensitivity: of the class label (where prevalence was measured)
    :param: specificity: of the class label (where prevalence was measured)

    :return: float adjusted prevalence
    """
    return round((prevalence_apparent + specificity - 1) / (sensitivity + specificity - 1), 5)
