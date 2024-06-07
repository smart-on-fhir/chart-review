"""Methods for showing config & calculated setup info."""

import argparse
import csv
import sys

import rich
import rich.box
import rich.table
import rich.tree

from chart_review import cli_utils, cohort, config, console_utils


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
        pad_edge=False,
        title="Annotations:",
        title_justify="left",
        title_style="bold",
    )
    for annotator in sorted(reader.note_range):
        notes = reader.note_range[annotator]
        chart_table.add_row(
            annotator,
            str(len(notes)),
            console_utils.pretty_note_range(notes),
        )
    console.print(chart_table)

    # Ignored charts
    if reader.ignored_notes:
        ignored_count = len(reader.ignored_notes)
        chart_word = "chart" if ignored_count == 1 else "charts"
        pretty_ranges = console_utils.pretty_note_range(reader.ignored_notes)
        console.print(
            f" Ignoring {ignored_count} {chart_word} ({pretty_ranges})",
            highlight=False,
            style="italic",
        )

    # Labels
    console.print()
    console.print("Labels:", style="bold")
    if reader.class_labels:
        console.print(", ".join(sorted(reader.class_labels, key=str.casefold)))
    else:
        console.print("None", style="italic", highlight=False)


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


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    parser.add_argument(
        "--ids", action="store_true", help="Prints a CSV of ID mappings (chart & FHIR IDs)"
    )
    parser.set_defaults(func=run_info)


def run_info(args: argparse.Namespace) -> None:
    proj_config = config.ProjectConfig(args.project_dir, config_path=args.config)
    reader = cohort.CohortReader(proj_config)
    if args.ids:
        print_ids(reader)
    else:
        print_info(reader)
