"""Methods for high-level accuracy calculations."""

import os

from chart_review import agree, cohort, common


def accuracy(reader: cohort.CohortReader, truth: str, annotator: str) -> None:
    """
    High-level accuracy calculation between two annotators.

    The results will be written to the project directory.

    :param reader: the cohort configuration
    :param truth: the truth annotator
    :param annotator: the other annotator to compare against truth
    """
    # Grab the intersection of ranges
    note_range = set(reader.config.note_ranges[truth])
    note_range &= set(reader.config.note_ranges[annotator])

    # All labels first
    table = agree.score_matrix(reader.confusion_matrix(truth, annotator, note_range))

    # Now do each labels separately
    for label in sorted(reader.class_labels):
        table[label] = agree.score_matrix(
            reader.confusion_matrix(truth, annotator, note_range, label)
        )

    # And write out the results
    output_stem = os.path.join(reader.project_dir, f"accuracy-{truth}-{annotator}")
    common.write_json(f"{output_stem}.json", table)
    print(f"Wrote {output_stem}.json")
    common.write_text(f"{output_stem}.csv", agree.csv_table(table, reader.class_labels))
    print(f"Wrote {output_stem}.csv")
