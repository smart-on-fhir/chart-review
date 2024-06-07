"""Methods for high-level accuracy calculations."""

import argparse
import os

import rich
import rich.table

from chart_review import agree, cli_utils, cohort, common, config, console_utils


def accuracy(reader: cohort.CohortReader, truth: str, annotator: str, save: bool = False) -> None:
    """
    High-level accuracy calculation between two annotators.

    The results will be written to the project directory.

    :param reader: the cohort configuration
    :param truth: the truth annotator
    :param annotator: the other annotator to compare against truth
    :param save: whether to write the results to disk vs just printing them
    """
    if truth not in reader.note_range:
        print(f"Unrecognized annotator '{truth}'")
        return
    if annotator not in reader.note_range:
        print(f"Unrecognized annotator '{annotator}'")
        return

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

    note_count = len(note_range)
    chart_word = "chart" if note_count == 1 else "charts"
    pretty_ranges = f" ({console_utils.pretty_note_range(note_range)})" if note_count > 0 else ""
    print(f"Comparing {note_count} {chart_word}{pretty_ranges}")
    print(f"Truth: {truth}")
    print(f"Annotator: {annotator}")
    print()

    if save:
        # Write the results out to disk
        output_stem = os.path.join(reader.project_dir, f"accuracy-{truth}-{annotator}")
        common.write_json(f"{output_stem}.json", table)
        print(f"Wrote {output_stem}.json")
        common.write_text(f"{output_stem}.csv", agree.csv_table(table, reader.class_labels))
        print(f"Wrote {output_stem}.csv")
    else:
        # Print the results out to the console
        rich_table = rich.table.Table(*agree.csv_header(), "Label", box=None, pad_edge=False)
        rich_table.add_row(*agree.csv_row_score(table), "*")
        for label in sorted(reader.class_labels):
            rich_table.add_row(*agree.csv_row_score(table[label]), label)
        rich.get_console().print(rich_table)


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    parser.add_argument(
        "--save", action="store_true", default=False, help="Write stats to CSV & JSON files"
    )
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator")
    parser.set_defaults(func=run_accuracy)


def run_accuracy(args: argparse.Namespace) -> None:
    proj_config = config.ProjectConfig(args.project_dir, config_path=args.config)
    reader = cohort.CohortReader(proj_config)
    accuracy(reader, args.truth_annotator, args.annotator, save=args.save)
