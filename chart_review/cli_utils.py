"""Helper methods for CLI parsing."""

import argparse
import csv
import sys

import rich.box
import rich.table

from chart_review import cohort, config


def add_project_args(parser: argparse.ArgumentParser, is_global: bool = False) -> None:
    group = parser.add_argument_group("configuration")
    group.add_argument(
        "--project-dir",
        "-p",
        default=None if is_global else argparse.SUPPRESS,
        metavar="DIR",
        help=(
            "directory holding project files, like labelstudio-export.json (default: current dir)"
        ),
    )
    group.add_argument(
        "--config",
        "-c",
        default=None if is_global else argparse.SUPPRESS,
        metavar="PATH",
        help="config file (default: [project-dir]/config.yaml)",
    )


def add_output_args(parser: argparse.ArgumentParser):
    """Returns an exclusive option group if you want to add custom output arguments"""
    group = parser.add_argument_group("output")
    exclusive = group.add_mutually_exclusive_group()
    exclusive.add_argument("--csv", action="store_true", help="print results in CSV format")
    return exclusive


def get_cohort_reader(args: argparse.Namespace) -> cohort.CohortReader:
    proj_config = config.ProjectConfig(project_dir=args.project_dir, config_path=args.config)
    return cohort.CohortReader(proj_config)


def create_table(*headers, dense: bool = False) -> rich.table.Table:
    """
    Creates a table with standard chart-review formatting.

    You can use your own table formatting if you have particular needs,
    but this should be your default table creator.
    """
    if dense:
        table = rich.table.Table(*headers, box=None, pad_edge=False)
    else:
        table = rich.table.Table(box=rich.box.ROUNDED)
        for header in headers:
            table.add_column(header, overflow="fold")
    return table


def print_table_as_csv(table: rich.table.Table) -> None:
    """Prints a Rich table as a CSV to stdout"""
    writer = csv.writer(sys.stdout)

    # First the headers
    headers = [str(col.header).lower().replace(" ", "_") for col in table.columns]
    writer.writerow(headers)

    # And then each row
    cells_by_row = zip(*[col.cells for col in table.columns])
    for row in cells_by_row:
        writer.writerow(row)
