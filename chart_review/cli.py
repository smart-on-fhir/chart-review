"""Run chart-review from the command-line"""

import argparse
import sys
from typing import Optional

from chart_review.commands import accuracy, default, frequency, ids, labels, mcnemar, mentions


def define_parser() -> argparse.ArgumentParser:
    """Fills out an argument parser with all the CLI options."""
    parser = argparse.ArgumentParser()
    default.make_subparser(parser)

    subparsers = parser.add_subparsers()
    accuracy.make_subparser(subparsers.add_parser("accuracy", help="calculate F1 and Kappa scores"))
    frequency.make_subparser(
        subparsers.add_parser("frequency", help="show counts of each text mention")
    )
    ids.make_subparser(subparsers.add_parser("ids", help="map Label Studio IDs to FHIR IDs"))
    labels.make_subparser(subparsers.add_parser("labels", help="show label usage by annotator"))
    mcnemar.make_subparser(subparsers.add_parser("mcnemar", help="calculate McNemar’s test"))
    mentions.make_subparser(subparsers.add_parser("mentions", help="show each mention of a label"))

    return parser


def main_cli(argv: Optional[list[str]] = None) -> None:
    """Main entrypoint that wraps all the core program logic"""
    try:
        parser = define_parser()
        args = parser.parse_args(argv)
        args.func(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main_cli()  # pragma: no cover
