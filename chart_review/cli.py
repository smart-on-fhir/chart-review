"""Run chart-review from the command-line"""

import argparse
import sys

from chart_review.commands import accuracy, default, ids, labels, mentions


def define_parser() -> argparse.ArgumentParser:
    """Fills out an argument parser with all the CLI options."""
    parser = argparse.ArgumentParser()
    default.make_subparser(parser)

    subparsers = parser.add_subparsers()
    accuracy.make_subparser(subparsers.add_parser("accuracy", help="calculate F1 and Kappa scores"))
    ids.make_subparser(subparsers.add_parser("ids", help="map Label Studio IDs to FHIR IDs"))
    labels.make_subparser(subparsers.add_parser("labels", help="show label usage by annotator"))
    mentions.make_subparser(subparsers.add_parser("mentions", help="show each mention of a label"))

    return parser


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
