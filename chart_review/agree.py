from collections.abc import Collection, Iterable
from typing import Union

from chart_review import types


def confusion_matrix(
    annotations: types.ProjectAnnotations,
    truth: str,
    annotator: str,
    note_range: Collection[int],
    labels: Iterable[str] = None,
) -> dict[str, list]:
    """
    Confusion Matrix (TP, FP, TN, FN)
    https://www.researchgate.net/figure/Calculation-of-sensitivity-specificity-and-positive-and-negative-predictive_fig1_49650721

    This is the rollup of counting each symptom only once, not multiple times for a single patient.
    :param annotations: prepared map of annotators & mentions
    :param truth: annotator to use as the ground truth
    :param annotator: another annotator to compare with truth
    :param note_range: collection of LabelStudio document ID
    :param labels: (optional) collection of labels to consider examining
    :return: Dict
        "TP": True Positives (agree on positive+ symptom)
        "FP": False Positives (annotator said positive+, truth said No)
        "FN": False Negative (truth said positive+, annotator said No)
        "TN": True Negative (truth and annotator both said No)
    """
    truth_mentions = annotations.mentions.get(truth, types.Mentions())
    annotator_mentions = annotations.mentions.get(annotator, types.Mentions())

    # Only examine labels that were used by any compared annotators at least once
    label_set = set()
    for _v in truth_mentions.values():
        label_set |= set(_v)
    for _v in annotator_mentions.values():
        label_set |= set(_v)
    if labels:
        label_set &= set(labels)

    TP = list()  # True Positive
    FP = list()  # False Positive
    FN = list()  # False Negative
    TN = list()  # True Negative

    for note_id in note_range:
        truth_note_mentions = truth_mentions.get(note_id, set())
        annotator_note_mentions = annotator_mentions.get(note_id, set())

        for label in sorted(label_set):
            key = {note_id: label}
            truth_positive = label in truth_note_mentions
            annotator_positive = label in annotator_note_mentions

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


def score_kappa(matrix: dict) -> float:
    """
    Computes Cohen kappa for pair-wise annotators.
    https://en.wikipedia.org/wiki/Cohen%27s_kappa

    :param matrix: confusion matrix with TN/TP/FN/FP values
    :return: Cohen kappa statistic
    """
    tp = len(matrix["TP"])  # true positive
    tn = len(matrix["TN"])  # true negative
    fp = len(matrix["FP"])  # false positive
    fn = len(matrix["FN"])  # false negative
    total = tp + tn + fp + fn

    # observed agreement A (Po)
    observed = (tp + tn) / total

    # expected agreement E (Pe)
    expected_pos = ((tp + fp) / total) * ((tp + fn) / total)
    expected_neg = ((tn + fp) / total) * ((tn + fn) / total)
    expected = expected_pos + expected_neg

    return (observed - expected) / (1 - expected)


def score_matrix(matrix: dict, sig_digits=3) -> dict:
    """
    Score F1 and Kappa measures with precision (PPV) and recall (sensitivity).
    F1 deliberately ignores "True Negatives" because TN inflates scoring (AUROC)
    @return: dict with keys {'f1', 'precision', 'recall'} vals are %score
    """
    true_pos = len(matrix["TP"])
    true_neg = len(matrix["TN"])
    false_pos = len(matrix["FP"])
    false_neg = len(matrix["FN"])

    if 0 == true_pos or 0 == true_neg:
        sens = 0
        spec = 0
        ppv = 0
        npv = 0
        f1 = 0
        kappa = 0
    else:
        sens = true_pos / (true_pos + false_neg)
        spec = true_neg / (true_neg + false_pos)
        ppv = true_pos / (true_pos + false_pos)
        npv = true_neg / (true_neg + false_neg)
        f1 = (2 * ppv * sens) / (ppv + sens)
        kappa = score_kappa(matrix)

    return {
        "F1": round(f1, sig_digits),
        "Sens": round(sens, sig_digits),
        "Spec": round(spec, sig_digits),
        "PPV": round(ppv, sig_digits),
        "NPV": round(npv, sig_digits),
        "Kappa": round(kappa, sig_digits),
        "TP": true_pos,
        "FP": false_pos,
        "FN": false_neg,
        "TN": true_neg,
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
    annotations: types.ProjectAnnotations,
    truth: str,
    annotator: str,
    note_range: Collection[int],
    labels: Iterable[str] = None,
) -> dict:
    """
    Score reliability of an annotator against a truth annotator.

    :param annotations: prepared map of annotators and mentions
    :param truth: annotator to use as the ground truth
    :param annotator: another annotator to compare with truth
    :param note_range: collection of LabelStudio document ID
    :param labels: (optional) set of labels to score
    :return: dict, keys f1, precision, recall and vals= %score
    """
    truth_matrix = confusion_matrix(annotations, truth, annotator, note_range, labels=labels)
    return score_matrix(truth_matrix)


def csv_table(score: dict, class_labels: Iterable):
    table = list()
    table.append(csv_header(False, True))
    table.append(csv_row_score(score, as_string=True))

    for label in sorted(class_labels):
        table.append(csv_row_score(score[label], label, as_string=True))
    return "\n".join(table) + "\n"


def csv_header(pick_label=False, as_string=False):
    """
    Table Header
    F1, PPV (precision), Recall (sensitivity), True Pos, False Pos, False Neg
    :param pick_label: default= None
    :return: header
    """
    as_list = ["F1", "Sens", "Spec", "PPV", "NPV", "Kappa", "TP", "FN", "TN", "FP"]

    if not as_string:
        return as_list

    header = as_list
    header.append(pick_label if pick_label else "Label")
    return "\t".join(header)


def csv_row_score(
    score: dict, pick_label: str = None, as_string: bool = False
) -> Union[str, list[str]]:
    """
    Table Row entry
    F1, PPV (precision), Recall (sensitivity), True Pos, False Pos, False Neg
    :param score: dict result from F1 scoring
    :param pick_label: default= None means '*' all classes
    :param as_string: whether to return a list of string scores or one single string
    :return: str representation of the score
    """
    row = [score[header] for header in csv_header()]
    row = [str(value) for value in row]

    if not as_string:
        return row

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
