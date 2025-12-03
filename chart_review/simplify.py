from chart_review import config, defines, studio


def simplify_export(
    export: studio.ExportFile, proj_config: config.ProjectConfig
) -> defines.ProjectAnnotations:
    """
    Label Studio outputs contain more info than needed for IAA and term_freq.

    * PHI raw physician note text is removed *

    :param export: exported json from Label Studio
    :param proj_config: project configuration
    :return: all project mentions parsed from the Label Studio export
    """
    annotations = defines.ProjectAnnotations()
    annotations.labels = proj_config.class_labels
    grab_all_labels = not annotations.labels

    for note in export.notes:
        for annot in note.annotations:
            if proj_config.annotators and annot.author not in proj_config.annotators:
                continue  # user specified an annotators config, and this one doesn't fit
            annotator = proj_config.annotators.get(annot.author, str(annot.author))

            # Grab all valid mentions for this annotator & note
            labels = defines.LabelSet()
            text_tags = []
            for mention in annot.mentions:
                labels |= mention.labels
                text_tags.append(defines.LabeledText(mention.text, mention.labels))

            if grab_all_labels:
                annotations.labels |= labels

            # Store these mentions in the main annotations list, by author & note
            annotator_mentions = annotations.mentions.setdefault(annotator, defines.Mentions())
            annotator_mentions[note.note_id] = labels
            annot_orig_text_tags = annotations.original_text_mentions.setdefault(annotator, {})
            annot_orig_text_tags[note.note_id] = text_tags

    return annotations


def _find_implied_labels(
    source_label: defines.Label,
    implied_label_mappings: defines.ImpliedLabels,
    found_labels: defines.LabelSet | None = None,
) -> defines.LabelSet:
    """
    Expands the source label into the set of all implied labels.

    Don't bother passing found_labels in, that's just a helper arg for recursion.
    """
    if found_labels is None:
        found_labels = set()

    if source_label in found_labels:
        return found_labels

    found_labels.add(source_label)
    for matcher, implied_labels in implied_label_mappings.items():
        if matcher.is_match(source_label):
            for implied_label in implied_labels:
                _find_implied_labels(
                    implied_label, implied_label_mappings, found_labels=found_labels
                )

    return found_labels


def _find_implied_mentions(
    mentions: defines.Mentions, implied_label_mappings: defines.ImpliedLabels
) -> defines.Mentions:
    """
    For every note, expands its labels into the set of all implied labels for that note.
    """
    found_mentions = defines.Mentions()

    for note_id, labels in mentions.items():
        implied_mentions = found_mentions.setdefault(note_id, set())
        for label in labels:
            implied_mentions |= _find_implied_labels(label, implied_label_mappings)

    return found_mentions


def _convert_grouped_mentions(
    mentions: defines.Mentions, grouped_label_mappings: defines.GroupedLabels
) -> defines.Mentions:
    """
    For every note, converts all labels in a group into one label for the group name.

    This is not recursive. (i.e. you can't have complicated grouping configs that combine)
    """
    final_mentions = defines.Mentions()

    for note_id, labels in mentions.items():
        for group_label, group_matcher in grouped_label_mappings.items():
            if matched := group_matcher.matches_in_set(labels):
                labels -= matched
                labels.add(group_label)
        final_mentions[note_id] = labels

    return final_mentions


def simplify_mentions(
    annotations: defines.ProjectAnnotations,
    *,
    implied_labels: defines.ImpliedLabels,
    grouped_labels: defines.GroupedLabels,
) -> None:
    # ** Expand all implied labels.
    annotations.mentions = {
        annotator: _find_implied_mentions(mentions, implied_labels)
        for annotator, mentions in annotations.mentions.items()
    }

    # ** Convert all grouped labels.
    # First, calculate the new set of valid labels, adding the group and removing the groupees
    annotations.labels |= set(grouped_labels.keys())
    annotations.labels.difference_update(
        *[m.matches_in_set(annotations.labels) for m in grouped_labels.values()]
    )
    # Next, convert old labels to the new group labels
    annotations.mentions = {
        annotator: _convert_grouped_mentions(mentions, grouped_labels)
        for annotator, mentions in annotations.mentions.items()
    }
