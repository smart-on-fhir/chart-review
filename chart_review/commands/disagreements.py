"""Command for disagreement review."""

import argparse

import rich
import rich.box
import rich.table
import rich.text

from chart_review import cli_utils, console_utils


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.add_argument("--with-ids", action="store_true", help="show each chart’s full IDs")
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator")
    parser.set_defaults(func=print_disagreements)


def print_disagreements(args: argparse.Namespace) -> None:
    """Shows disagreement of labels between two annotators."""
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
    matrices = {
        label: reader.confusion_matrix(truth, annotator, note_range, label) for label in labels
    }

    console = rich.get_console()

    if args.with_ids:
        table = cli_utils.create_table("Chart ID", "FHIR ID", "Anon ID", "Label", "Classification")
    else:
        table = cli_utils.create_table("Chart ID", "Label", "Classification")

    for note in sorted(reader.ls_export.notes, key=lambda x: x.note_id):
        if note.note_id not in note_range:
            continue

        ids = []

        # Grab encounters first
        orig_id = note.encounter_id and f"Encounter/{note.encounter_id}"
        anon_id = note.anon_encounter_id and f"Encounter/{note.anon_encounter_id}"
        if orig_id or anon_id:
            ids.append((orig_id, anon_id))

        # Now each DocRef ID
        for orig_id, anon_id in note.docref_mappings.items():
            ids.append((orig_id, anon_id))

        if not ids:
            ids.append(("", ""))

        table.add_section()
        for label in labels:
            for classification in ["FN", "FP"]:
                label_key = (note.note_id, label.label, label.sublabel_name)
                if label_key in matrices[label][classification]:
                    class_text = rich.text.Text(classification)
                    if args.with_ids:
                        for id_pair in ids:
                            table.add_row(
                                str(note.note_id), id_pair[0], id_pair[1], str(label), class_text
                            )
                    else:
                        table.add_row(str(note.note_id), str(label), class_text)
                    break

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

    console.print()
    console.print(table)

    console_utils.print_ignored_labels(reader, annotators={truth, annotator})
