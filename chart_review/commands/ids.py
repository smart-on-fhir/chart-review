import argparse
import csv
import sys

from chart_review import cli_utils


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    parser.set_defaults(func=print_ids)


def print_ids(args: argparse.Namespace) -> None:
    """
    Prints a mapping of all project IDs.

    Currently, this writes a CSV file to stdout. In the future, this could get fancier.
    At the time of writing, it wasn't clear how to present the information in a way that
    sensible to a casual console user - so I went with the more technical-oriented CSV file.
    """
    reader = cli_utils.get_cohort_reader(args)

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
