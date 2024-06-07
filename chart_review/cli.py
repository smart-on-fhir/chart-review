"""Run chart-review from the command-line"""

import argparse
import sys

from chart_review.commands import accuracy, info


def define_parser() -> argparse.ArgumentParser:
    """Fills out an argument parser with all the CLI options."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)

    accuracy.make_subparser(subparsers.add_parser("accuracy"))
    info.make_subparser(subparsers.add_parser("info"))

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
