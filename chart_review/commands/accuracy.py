"""Methods for high-level accuracy calculations."""

import argparse
import os

import rich
import rich.box
import rich.table
import rich.text

from chart_review import agree, cli_utils, common, console_utils


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    output_group = cli_utils.add_output_args(parser)
    output_group.add_argument("--save", action="store_true", help=argparse.SUPPRESS)
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

    labels = sorted(reader.class_labels, key=str.casefold)

    # Calculate confusion matrices
    matrices = {None: reader.confusion_matrix(truth, annotator, note_range)}
    for label in labels:
        matrices[label] = reader.confusion_matrix(truth, annotator, note_range, label)

    # Now score them
    scores = {None: agree.score_matrix(matrices[None])}
    for label in labels:
        scores[label] = agree.score_matrix(matrices[label])

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
                        table.add_row(str(note_id), label, class_text)
                        break
    else:
        # Normal F1/Kappa scores
        table = cli_utils.create_table(*agree.csv_header(), "Label", dense=True)
        table.add_row(*agree.csv_row_score(scores[None]), "*")
        for label in labels:
            table.add_row(*agree.csv_row_score(scores[label]), label)

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
        macro_f1 = sum(scores[label]["F1"] for label in labels) / len(labels)
        console.print(f"Macro F1: {round(macro_f1, 3)}")

    console.print()

    if args.save:  # deprecated/hidden since 2.0, but still supported for now
        output_stem = os.path.join(reader.project_dir, f"accuracy-{truth}-{annotator}")

        # Round before we hit disk
        for label_scores in scores.values():
            for key, value in label_scores.items():
                label_scores[key] = round(value, 3)

        # JSON: Historically, this has been formatted with the global label results intermixed
        # with the specific label names, so reproduce that historical formatting here.
        # Note: this could bite us if the user ever has a label like "Kappa", which is why the
        # above code avoids intermixing, but we'll keep this as-is for now.
        scores.update(scores[None])
        del scores[None]

        common.write_json(f"{output_stem}.json", scores)
        console.print(f"Wrote {output_stem}.json")

        # CSV: we should really use a .tsv suffix here, but keeping .csv for historical reasons
        common.write_text(f"{output_stem}.csv", agree.csv_table(scores, reader.class_labels))
        console.print(f"Wrote {output_stem}.csv")
    else:
        console.print(table)
