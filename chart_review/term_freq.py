from ctakesclient.typesystem import Span

from chart_review import types


def calc_term_freq(annotations: types.ProjectAnnotations, annotator: str) -> dict:
    """
    Calculate the frequency of TERMS highlighted for each LABEL (Cough, Dyspnea, etc).
    :param annotations: prepared map of mentions
    :param annotator: an annotator name
    :return: dict key=TERM val= {label, list of chart_id}
    """
    original_text_mentions = annotations.original_text_mentions.get(annotator, {})

    term_freq = {}
    for note_id, text_labels in original_text_mentions.items():
        for text_label in text_labels:
            if not text_label.text:
                continue

            term = text_label.text.upper()
            term_counts = term_freq.setdefault(term, {})

            for label in text_label.labels:
                term_label_counts = term_counts.setdefault(label, [])
                term_label_counts.append(note_id)

    return term_freq


def calc_term_label_confusion(term_freq: dict) -> dict:
    """
    Calculate term mentions that have more than one label associated.
    Usually due to user error in LabelStudio.

    @param term_freq: output of 'calc_term_freq'
    @return: dict filtered by only confusing TERMs
    """
    confusing = dict()
    for term in term_freq.keys():
        if len(term_freq[term].keys()) > 1:
            confusing[term] = term_freq[term]
    return confusing


def calc_label_freq(term_freq: dict) -> dict:
    unique = dict()
    for term in term_freq.keys():
        for label in term_freq[term].keys():
            if label not in unique.keys():
                unique[label] = dict()
            if term not in unique[label].keys():
                unique[label][term] = list()
            for note_id in term_freq[term][label]:
                unique[label][term].append(note_id)
    tf = dict()
    for label in unique.keys():
        for term in unique[label].keys():
            if label not in tf.keys():
                tf[label] = dict()
            tf[label][term] = len(unique[label][term])
    return tf


def intersect(span1: Span, span2: Span) -> set:
    """
    TODO Refactor to ctakes-client:
    https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/issues/55

    Get char text positions where overlaps exist.

    :param span1: 1st text Span
    :param span2: 2nd text Span
    :return: set of CHAR positions (convertible to range or Span)
    """
    range1 = range(span1.begin, span1.end)
    range2 = range(span2.begin, span2.end)
    return set(range1).intersection(set(range2))


def overlaps(span1: Span, span2: Span, min_length=2, max_length=20) -> bool:
    """
    TODO Refactor to ctakes-client:
    https://github.com/Machine-Learning-for-Medical-Language/ctakes-client-py/issues/55

    True/False text overlap exists between two spans of 'highlighted' text.

    :param span1: 1st text Span
    :param span2: 2nd text Span
    :param min_length: MIN length of comparison, default 2 chars
    :param max_length: MAX length of comparison, default 20 chars (or equals)
    :return: true/false the two spans overlap
    """
    shared = intersect(span1, span2)
    if len(shared) == len(range(span1.begin, span1.end)):
        return True
    elif (len(shared) >= min_length) and (len(shared) <= max_length):
        return True
    else:
        return False
