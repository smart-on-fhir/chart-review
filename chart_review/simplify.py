import re
from collections.abc import Container

from chart_review import config, types


def simplify_export(
    exported_json: list[dict], proj_config: config.ProjectConfig
) -> types.ProjectAnnotations:
    """
    Label Studio outputs contain more info than needed for IAA and term_freq.

    * PHI raw physician note text is removed *

    :param exported_json: exported json from Label Studio
    :param proj_config: project configuration
    :return: all project mentions parsed from the Label Studio export
    """
    annotations = types.ProjectAnnotations()
    annotations.labels = proj_config.class_labels

    for entry in exported_json:
        note_id = int(entry.get("id"))

        for annot in entry.get("annotations"):
            completed_by = annot.get("completed_by")
            if completed_by not in proj_config.annotators:
                continue  # we don't know who this is!

            # Grab all valid mentions for this annotator & note
            labels = types.LabelSet()
            text_tags = []
            for result in annot.get("result"):
                result_value = result.get("value", {})
                result_text = result_value.get("text")
                result_labels = set(result_value.get("labels", []))

                labels |= result_labels
                text_tags.append(types.LabeledText(result_text, result_labels))

            # Store these mentions in the main annotations list, by author & note
            annotator = proj_config.annotators[completed_by]
            annotator_mentions = annotations.mentions.setdefault(annotator, types.Mentions())
            annotator_mentions[note_id] = labels
            annot_orig_text_tags = annotations.original_text_mentions.setdefault(annotator, {})
            annot_orig_text_tags[note_id] = text_tags

    return annotations


def _find_implied_labels(
    source_label: str, implied_label_mappings: types.ImpliedLabels, found_labels: set[str] = None
) -> set[str]:
    """
    Expands the source label into the set of all implied labels.

    Don't bother passing found_labels in, that's just a helper arg for recursion.
    """
    if found_labels is None:
        found_labels = set()

    if source_label in found_labels:
        return found_labels

    found_labels.add(source_label)
    for implied_label in implied_label_mappings.get(source_label, []):
        _find_implied_labels(implied_label, implied_label_mappings, found_labels=found_labels)

    return found_labels


def _find_implied_mentions(
    mentions: types.Mentions, implied_label_mappings: types.ImpliedLabels
) -> types.Mentions:
    """
    For every note, expands its labels into the set of all implied labels for that note.
    """
    found_mentions = types.Mentions()

    for note_id, labels in mentions.items():
        implied_mentions = found_mentions.setdefault(note_id, set())
        for label in labels:
            implied_mentions |= _find_implied_labels(label, implied_label_mappings)

    return found_mentions


def _convert_grouped_mentions(
    mentions: types.Mentions, grouped_label_mappings: types.GroupedLabels
) -> types.Mentions:
    """
    For every note, converts all labels in a group into one label for the group name.

    This is not recursive. (i.e. you can't have complicated grouping configs that combine)
    """
    final_mentions = types.Mentions()

    for note_id, labels in mentions.items():
        for group_name, group_members in grouped_label_mappings.items():
            if labels & group_members:
                labels -= group_members
                labels.add(group_name)
        final_mentions[note_id] = labels

    return final_mentions


def simplify_mentions(
    annotations: types.ProjectAnnotations,
    *,
    implied_labels: types.ImpliedLabels,
    grouped_labels: types.GroupedLabels,
) -> None:
    # ** Expand all implied labels.
    annotations.mentions = {
        annotator: _find_implied_mentions(mentions, implied_labels)
        for annotator, mentions in annotations.mentions.items()
    }

    # ** Convert all grouped labels.
    # First, calculate the new set of valid labels
    annotations.labels |= set(grouped_labels.keys())
    annotations.labels = annotations.labels.difference(*grouped_labels.values())
    # Next, convert old labels to the new group labels
    annotations.mentions = {
        annotator: _convert_grouped_mentions(mentions, grouped_labels)
        for annotator, mentions in annotations.mentions.items()
    }
