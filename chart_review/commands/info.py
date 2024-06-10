"""Methods for showing config & calculated setup info."""

import argparse
import csv
import sys

import rich
import rich.box
import rich.table
import rich.text
import rich.tree

from chart_review import cli_utils, cohort, config, console_utils, types


def print_info(reader: cohort.CohortReader) -> None:
    """
    Show project information on the console.

    :param reader: the cohort configuration
    """
    console = rich.get_console()

    # Charts
    chart_table = rich.table.Table(
        "Annotator",
        "Chart Count",
        "Chart IDs",
        box=rich.box.ROUNDED,
    )
    for annotator in sorted(reader.note_range):
        notes = reader.note_range[annotator]
        chart_table.add_row(
            annotator,
            str(len(notes)),
            console_utils.pretty_note_range(notes),
        )

    console.print(chart_table)
    print_ignored_charts(reader)


def print_ids(reader: cohort.CohortReader) -> None:
    """
    Prints a mapping of all project IDs.

    Currently, this writes a CSV file to stdout. In the future, this could get fancier.
    At the time of writing, it wasn't clear how to present the information in a way that
    sensible to a casual console user - so I went with the more technical-oriented CSV file.
    """
    writer = csv.writer(sys.stdout)
    writer.writerow(["chart_id", "original_fhir_id", "anonymized_fhir_id"])

    # IDS
    for chart in reader.ls_export:
        chart_id = str(chart["id"])
        chart_data = chart.get("data", {})
        printed = False

        # Grab encounters first
        orig_id = f"Encounter/{chart_data['enc_id']}" if "enc_id" in chart_data else ""
        anon_id = f"Encounter/{chart_data['anon_id']}" if "anon_id" in chart_data else ""
        if orig_id or anon_id:
            writer.writerow([chart_id, orig_id, anon_id])
            printed = True

        # Now each DocRef ID
        for orig_id, anon_id in chart_data.get("docref_mappings", {}).items():
            writer.writerow(
                [chart_id, f"DocumentReference/{orig_id}", f"DocumentReference/{anon_id}"]
            )
            printed = True

        if not printed:
            # Guarantee that every Chart ID shows up at least once - so it's clearer that the
            # chart ID is included in the Label Studio export but that it does not have any
            # IDs mapped to it.
            writer.writerow([chart_id, None, None])


def print_labels(reader: cohort.CohortReader) -> None:
    """
    Show label information on the console.

    :param reader: the cohort configuration
    """
    # Calculate all label counts for each annotator
    label_names = sorted(reader.class_labels, key=str.casefold)
    label_notes: dict[str, dict[str, types.NoteSet]] = {}  # annotator -> label -> note IDs
    any_annotator_note_sets: dict[str, types.NoteSet] = {}
    for annotator, mentions in reader.annotations.mentions.items():
        label_notes[annotator] = {}
        for name in label_names:
            note_ids = {note_id for note_id, labels in mentions.items() if name in labels}
            label_notes[annotator][name] = note_ids
            any_annotator_note_sets.setdefault(name, types.NoteSet()).update(note_ids)

    label_table = rich.table.Table(
        "Annotator",
        "Chart Count",
        "Label",
        box=rich.box.ROUNDED,
    )

    # First add summary entries, for counts across the union of all annotators
    for name in label_names:
        count = str(len(any_annotator_note_sets.get(name, {})))
        label_table.add_row(rich.text.Text("Any", style="italic"), count, name)

    # Now do each annotator as their own little boxed section
    for annotator in sorted(label_notes.keys(), key=str.casefold):
        label_table.add_section()
        for name, note_set in label_notes[annotator].items():
            count = str(len(note_set))
            label_table.add_row(annotator, count, name)

    rich.get_console().print(label_table)
    print_ignored_charts(reader)


def print_ignored_charts(reader: cohort.CohortReader):
    """Prints a line about ignored charts, suitable for underlying a table"""
    if not reader.ignored_notes:
        return

    ignored_count = len(reader.ignored_notes)
    chart_word = "chart" if ignored_count == 1 else "charts"
    pretty_ranges = console_utils.pretty_note_range(reader.ignored_notes)
    rich.get_console().print(
        f"  Ignoring {ignored_count} {chart_word} ({pretty_ranges})",
        highlight=False,
        style="italic",
    )


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--ids", action="store_true", help="Prints a CSV of ID mappings (chart & FHIR IDs)"
    )
    mode.add_argument("--labels", action="store_true", help="Prints label info and usage")
    parser.set_defaults(func=run_info)


def run_info(args: argparse.Namespace) -> None:
    proj_config = config.ProjectConfig(args.project_dir, config_path=args.config)
    reader = cohort.CohortReader(proj_config)
    if args.ids:
        print_ids(reader)
    elif args.labels:
        print_labels(reader)
    else:
        print_info(reader)
