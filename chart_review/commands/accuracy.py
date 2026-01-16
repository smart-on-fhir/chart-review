"""Methods for high-level accuracy calculations."""

import argparse
import math

import rich
import rich.box
import rich.table
import rich.text

from chart_review import agree, cli_utils, console_utils, defines


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.add_argument("--verbose", action="store_true", help="show each chart’s labels")
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator")
    parser.set_defaults(func=print_accuracy)


def print_accuracy(args: argparse.Namespace) -> None:
    """
    High-level accuracy calculation between two annotators.

    The results will be written to the project directory.
    """
    reader = cli_utils.get_cohort_reader(args)
    truth = args.truth_annotator
    annotator = args.annotator

    if truth not in reader.note_range:
        raise ValueError(f"Unrecognized annotator '{truth}'")
    if annotator not in reader.note_range:
        raise ValueError(f"Unrecognized annotator '{annotator}'")

    if truth == annotator:
        raise ValueError("Can’t compare the same annotator with themselves.")

    # Grab the intersection of ranges
    note_range = set(reader.note_range[truth])
    note_range &= set(reader.note_range[annotator])

    labels = sorted(reader.class_labels)

    # Calculate confusion matrices
    matrices = {None: reader.confusion_matrix(truth, annotator, note_range)}
    for label in labels:
        matrices[label] = reader.confusion_matrix(truth, annotator, note_range, label)
        # Add an aggregate row for any sublabel groupings
        if label.sublabel_name:
            matcher = defines.LabelMatcher(f"{label.label}|{label.sublabel_name}|*")
            if matcher not in matrices:
                matrices[matcher] = reader.confusion_matrix(truth, annotator, note_range, matcher)

    # Now score them
    scores = {key: agree.score_matrix(matrix) for key, matrix in matrices.items()}

    console = rich.get_console()

    if args.verbose:
        # Print a table of each chart/label combo - useful for reviewing where an annotator
        # went wrong.
        table = cli_utils.create_table("Chart ID", "Label", "Classification")
        for note_id in sorted(note_range):
            table.add_section()
            for label in labels:
                for classification in ["TN", "TP", "FN", "FP"]:
                    if {note_id: label} in matrices[label][classification]:
                        style = "bold" if classification[0] == "F" else None  # highlight errors
                        class_text = rich.text.Text(classification, style=style)
                        table.add_row(str(note_id), str(label), class_text)
                        break
    else:
        # Normal F1/Kappa scores
        table = cli_utils.create_table(*agree.csv_header(), "Label", dense=True)
        table.add_row(*agree.csv_row_score(scores[None]), "*")
        for label in labels:
            # Add an aggregate row for any sublabel groupings
            if label.sublabel_name:
                matcher = defines.LabelMatcher(f"{label.label}|{label.sublabel_name}|*")
                if matcher in scores:
                    wildcard_label = defines.Label(label.label, label.sublabel_name, "*")
                    table.add_row(*agree.csv_row_score(scores[matcher]), str(wildcard_label))
                    del scores[matcher]
            table.add_row(*agree.csv_row_score(scores[label]), str(label))

    if args.csv:
        cli_utils.print_table_as_csv(table)
        return

    # OK we aren't printing a CSV file to stdout, so we can include a bit more explanation
    # as a little header to the real results.
    note_count = len(note_range)
    chart_word = "chart" if note_count == 1 else "charts"
    pretty_ranges = f" ({console_utils.pretty_note_range(note_range)})" if note_count > 0 else ""
    console.print(f"Comparing {note_count} {chart_word}{pretty_ranges}")
    console.print(f"Truth: {truth}")
    console.print(f"Annotator: {annotator}")

    if not args.verbose and labels:
        # Calculate Macro F1 as a convenience
        valid_f1s = [scores[label]["F1"] for label in labels if not math.isnan(scores[label]["F1"])]
        macro_f1 = sum(valid_f1s) / len(valid_f1s) if valid_f1s else "-"
        console.print(f"Macro F1: {agree.float_to_str(macro_f1)}")

    console.print()
    console.print(table)
