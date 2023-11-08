"""Run chart-review from the command-line"""

import argparse
import sys

from chart_review import cohort
from chart_review.commands.accuracy import accuracy


###############################################################################
#
# CLI Helpers
#
###############################################################################


def add_project_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Directory holding project files, like config.yaml and labelstudio-export.json (default: current dir)",
    )


def define_parser() -> argparse.ArgumentParser:
    """Fills out an argument parser with all the CLI options."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    add_accuracy_subparser(subparsers)

    return parser


###############################################################################
#
# Accuracy
#
###############################################################################


def add_accuracy_subparser(subparsers) -> None:
    parser = subparsers.add_parser("accuracy")
    add_project_args(parser)
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator")
    parser.set_defaults(func=run_accuracy)


def run_accuracy(args: argparse.Namespace) -> None:
    reader = cohort.CohortReader(args.project_dir)
    accuracy(reader, args.truth_annotator, args.annotator)


###############################################################################
#
# Main CLI entrypoints
#
###############################################################################


def main_cli(argv: list[str] = None) -> None:
    """Main entrypoint that wraps all the core program logic"""
    try:
        parser = define_parser()
        args = parser.parse_args(argv)
        args.func(args)
    except Exception as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main_cli()
