"""Run chart-review from the command-line"""

import argparse
import os
import sys

from chart_review import agree, cohort, common


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
    parser.add_argument("one")
    parser.add_argument("two")
    parser.add_argument("base")
    parser.set_defaults(func=run_accuracy)


def run_accuracy(args: argparse.Namespace) -> None:
    reader = cohort.CohortReader(args.project_dir)

    first_ann = args.one
    second_ann = args.two
    base_ann = args.base

    # Grab ranges
    first_range = reader.config.note_ranges[first_ann]
    second_range = reader.config.note_ranges[second_ann]

    # All labels first
    first_matrix = reader.confusion_matrix(first_ann, base_ann, first_range)
    second_matrix = reader.confusion_matrix(second_ann, base_ann, second_range)
    whole_matrix = agree.append_matrix(first_matrix, second_matrix)
    table = agree.score_matrix(whole_matrix)

    # Now do each labels separately
    for label in reader.class_labels:
        first_matrix = reader.confusion_matrix(first_ann, base_ann, first_range, label)
        second_matrix = reader.confusion_matrix(second_ann, base_ann, second_range, label)
        whole_matrix = agree.append_matrix(first_matrix, second_matrix)
        table[label] = agree.score_matrix(whole_matrix)

    # And write out the results
    output_stem = os.path.join(reader.project_dir, f"accuracy-{first_ann}-{second_ann}-{base_ann}")
    common.write_json(f"{output_stem}.json", table)
    print(f"Wrote {output_stem}.json")
    common.write_text(f"{output_stem}.csv", agree.csv_table(table, reader.class_labels))
    print(f"Wrote {output_stem}.csv")


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
