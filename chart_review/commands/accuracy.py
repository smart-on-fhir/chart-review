"""Methods for high-level accuracy calculations."""

import os

import rich
import rich.table

from chart_review import agree, cohort, common


def accuracy(reader: cohort.CohortReader, truth: str, annotator: str, save: bool = False) -> None:
    """
    High-level accuracy calculation between two annotators.

    The results will be written to the project directory.

    :param reader: the cohort configuration
    :param truth: the truth annotator
    :param annotator: the other annotator to compare against truth
    :param save: whether to write the results to disk vs just printing them
    """
    # Grab the intersection of ranges
    note_range = set(reader.note_range[truth])
    note_range &= set(reader.note_range[annotator])

    # All labels first
    table = agree.score_matrix(reader.confusion_matrix(truth, annotator, note_range))

    # Now do each labels separately
    for label in sorted(reader.class_labels):
        table[label] = agree.score_matrix(
            reader.confusion_matrix(truth, annotator, note_range, label)
        )

    result_name = f"accuracy-{truth}-{annotator}"
    if save:
        # Write the results out to disk
        output_stem = os.path.join(reader.project_dir, result_name)
        common.write_json(f"{output_stem}.json", table)
        print(f"Wrote {output_stem}.json")
        common.write_text(f"{output_stem}.csv", agree.csv_table(table, reader.class_labels))
        print(f"Wrote {output_stem}.csv")
    else:
        # Print the results out to the console
        print(f"{result_name}:")
        rich_table = rich.table.Table(*agree.csv_header(), "Label", box=None, pad_edge=False)
        rich_table.add_row(*agree.csv_row_score(table), "*")
        for label in sorted(reader.class_labels):
            rich_table.add_row(*agree.csv_row_score(table[label]), label)
        rich.get_console().print(rich_table)
