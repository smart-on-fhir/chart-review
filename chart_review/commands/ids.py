import argparse

import rich.table

from chart_review import cli_utils


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.set_defaults(func=print_ids)


def print_ids(args: argparse.Namespace) -> None:
    """
    Prints a mapping of all project IDs.

    Currently, this writes a CSV file to stdout. In the future, this could get fancier.
    At the time of writing, it wasn't clear how to present the information in a way that
    sensible to a casual console user - so I went with the more technical-oriented CSV file.
    """
    reader = cli_utils.get_cohort_reader(args)

    table = cli_utils.create_table("Chart ID", "Original FHIR ID", "Anonymized FHIR ID")

    for chart in reader.ls_export:
        chart_id = str(chart["id"])
        chart_data = chart.get("data", {})
        printed = False

        # Grab encounters first
        if "encounter_id" in chart_data:
            orig_id = f"Encounter/{chart_data['encounter_id']}"
        elif "enc_id" in chart_data:
            orig_id = f"Encounter/{chart_data['enc_id']}"
        else:
            orig_id = ""
        if "anon_encounter_id" in chart_data:
            anon_id = f"Encounter/{chart_data['anon_encounter_id']}"
        elif "anon_id" in chart_data:
            anon_id = f"Encounter/{chart_data['anon_id']}"
        else:
            anon_id = ""
        if orig_id or anon_id:
            table.add_row(chart_id, orig_id, anon_id)
            printed = True

        # Now each DocRef ID
        for orig_id, anon_id in chart_data.get("docref_mappings", {}).items():
            table.add_row(chart_id, f"DocumentReference/{orig_id}", f"DocumentReference/{anon_id}")
            printed = True

        if not printed:
            # Guarantee that every Chart ID shows up at least once - so it's clearer that the
            # chart ID is included in the Label Studio export but that it does not have any
            # IDs mapped to it.
            table.add_row(chart_id, None, None)

    if args.csv:
        cli_utils.print_table_as_csv(table)
    else:
        rich.get_console().print(table)
