"""Methods for high-level accuracy calculations."""

import argparse
import os

import rich
import rich.box
import rich.table
import rich.text

from chart_review import agree, cli_utils, cohort, common, config, console_utils


def accuracy(
    reader: cohort.CohortReader,
    truth: str,
    annotator: str,
    save: bool = False,
    verbose: bool = False,
) -> None:
    """
    High-level accuracy calculation between two annotators.

    The results will be written to the project directory.

    :param reader: the cohort configuration
    :param truth: the truth annotator
    :param annotator: the other annotator to compare against truth
    :param save: whether to write the results to disk vs just printing them
    :param verbose: whether to print per-chart/per-label classifications
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

    labels = sorted(reader.class_labels, key=str.casefold)

    # Calculate confusion matrices
    matrices = {None: reader.confusion_matrix(truth, annotator, note_range)}
    for label in labels:
        matrices[label] = reader.confusion_matrix(truth, annotator, note_range, label)

    # Now score them
    scores = agree.score_matrix(matrices[None])
    for label in labels:
        scores[label] = agree.score_matrix(matrices[label])

    console = rich.get_console()

    note_count = len(note_range)
    chart_word = "chart" if note_count == 1 else "charts"
    pretty_ranges = f" ({console_utils.pretty_note_range(note_range)})" if note_count > 0 else ""
    console.print(f"Comparing {note_count} {chart_word}{pretty_ranges}")
    console.print(f"Truth: {truth}")
    console.print(f"Annotator: {annotator}")

    console.print()
    if save:
        # Write the results out to disk
        output_stem = os.path.join(reader.project_dir, f"accuracy-{truth}-{annotator}")
        common.write_json(f"{output_stem}.json", scores)
        console.print(f"Wrote {output_stem}.json")
        common.write_text(f"{output_stem}.csv", agree.csv_table(scores, reader.class_labels))
        console.print(f"Wrote {output_stem}.csv")
    else:
        # Print the results out to the console
        rich_table = rich.table.Table(*agree.csv_header(), "Label", box=None, pad_edge=False)
        rich_table.add_row(*agree.csv_row_score(scores), "*")
        for label in labels:
            rich_table.add_row(*agree.csv_row_score(scores[label]), label)
        console.print(rich_table)

    if verbose:
        # Print a table of each chart/label combo - useful for reviewing where an annotator
        # went wrong.
        verbose_table = rich.table.Table(
            "Chart ID", "Label", "Classification", box=rich.box.ROUNDED
        )
        for note_id in sorted(note_range):
            verbose_table.add_section()
            for label in labels:
                for classification in ["TN", "TP", "FN", "FP"]:
                    if {note_id: label} in matrices[label][classification]:
                        style = "bold" if classification[0] == "F" else None  # highlight errors
                        class_text = rich.text.Text(classification, style=style)
                        verbose_table.add_row(str(note_id), label, class_text)
                        break
        console.print()
        console.print(verbose_table)


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    parser.add_argument("--save", action="store_true", help="Write stats to CSV & JSON files")
    parser.add_argument("--verbose", action="store_true", help="Explain each chart’s labels")
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator")
    parser.set_defaults(func=run_accuracy)


def run_accuracy(args: argparse.Namespace) -> None:
    proj_config = config.ProjectConfig(args.project_dir, config_path=args.config)
    reader = cohort.CohortReader(proj_config)
    accuracy(reader, args.truth_annotator, args.annotator, save=args.save, verbose=args.verbose)
