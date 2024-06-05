"""Run chart-review from the command-line"""

import argparse
import sys

from chart_review import cohort, config
from chart_review.commands.accuracy import accuracy
from chart_review.commands.info import info


###############################################################################
#
# CLI Helpers
#
###############################################################################


def add_project_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project-dir",
        default=".",
        metavar="DIR",
        help=(
            "Directory holding project files, "
            "like labelstudio-export.json (default: current dir)"
        ),
    )
    parser.add_argument(
        "--config", "-c", metavar="PATH", help="Config file (default: [project-dir]/config.yaml)"
    )


def define_parser() -> argparse.ArgumentParser:
    """Fills out an argument parser with all the CLI options."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    add_accuracy_subparser(subparsers)
    add_info_subparser(subparsers)

    return parser


###############################################################################
#
# Accuracy
#
###############################################################################


def add_accuracy_subparser(subparsers) -> None:
    parser = subparsers.add_parser("accuracy")
    add_project_args(parser)
    parser.add_argument("--save", action="store_true", default=False)
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator")
    parser.set_defaults(func=run_accuracy)


def run_accuracy(args: argparse.Namespace) -> None:
    proj_config = config.ProjectConfig(args.project_dir, config_path=args.config)
    reader = cohort.CohortReader(proj_config)
    accuracy(reader, args.truth_annotator, args.annotator, save=args.save)


###############################################################################
#
# Info
#
###############################################################################


def add_info_subparser(subparsers) -> None:
    parser = subparsers.add_parser("info")
    add_project_args(parser)
    parser.set_defaults(func=run_info)


def run_info(args: argparse.Namespace) -> None:
    proj_config = config.ProjectConfig(args.project_dir, config_path=args.config)
    reader = cohort.CohortReader(proj_config)
    info(reader)


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
