"""Methods for high-level accuracy calculations."""

import os

from chart_review import agree, cohort, common


def accuracy(reader: cohort.CohortReader, first_ann: str, second_ann: str, base_ann: str) -> None:
    """
    High-level accuracy calculation between three reviewers.

    The results will be written to the project directory.

    :param reader: the cohort configuration
    :param first_ann: the first annotator to compare
    :param second_ann: the second annotator to compare
    :param base_ann: the base annotator to compare the others against
    """
    # Grab ranges
    first_range = reader.config.note_ranges[first_ann]
    second_range = reader.config.note_ranges[second_ann]

    # All labels first
    first_matrix = reader.confusion_matrix(first_ann, base_ann, first_range)
    second_matrix = reader.confusion_matrix(second_ann, base_ann, second_range)
    whole_matrix = agree.append_matrix(first_matrix, second_matrix)
    table = agree.score_matrix(whole_matrix)

    # Now do each labels separately
    for label in reader.class_labels:
        first_matrix = reader.confusion_matrix(first_ann, base_ann, first_range, label)
        second_matrix = reader.confusion_matrix(second_ann, base_ann, second_range, label)
        whole_matrix = agree.append_matrix(first_matrix, second_matrix)
        table[label] = agree.score_matrix(whole_matrix)

    # And write out the results
    output_stem = os.path.join(reader.project_dir, f"accuracy-{first_ann}-{second_ann}-{base_ann}")
    common.write_json(f"{output_stem}.json", table)
    print(f"Wrote {output_stem}.json")
    common.write_text(f"{output_stem}.csv", agree.csv_table(table, reader.class_labels))
    print(f"Wrote {output_stem}.csv")
