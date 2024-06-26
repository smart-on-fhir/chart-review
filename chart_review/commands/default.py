"""Methods for showing config & calculated setup info."""

import argparse

import rich
import rich.box
import rich.table

import chart_review
from chart_review import cli_utils, console_utils


def print_info(args: argparse.Namespace) -> None:
    """Show project information on the console."""
    reader = cli_utils.get_cohort_reader(args)
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
            f"{len(notes):,}",
            console_utils.pretty_note_range(notes),
        )

    console.print(chart_table)
    console_utils.print_ignored_charts(reader)

    console.print()
    console.print("Pass --help to see more options.")


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser, is_global=True)
    parser.add_argument(
        "--version",
        action="version",
        version=f"chart-review {chart_review.__version__}",
    )
    parser.set_defaults(func=print_info)
