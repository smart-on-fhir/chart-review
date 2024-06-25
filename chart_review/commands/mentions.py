import argparse

import rich
import rich.box
import rich.table
import rich.text

from chart_review import cli_utils, console_utils, types


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.set_defaults(func=print_mentions)


def print_mentions(args: argparse.Namespace) -> None:
    """
    Print Label Studio export's mentions (text associated with the label).
    """
    reader = cli_utils.get_cohort_reader(args)

    table = cli_utils.create_table("Annotator", "Chart ID", "Mention", "Label")

    for annotator in sorted(reader.annotations.original_text_mentions, key=str.casefold):
        table.add_section()
        mentions = reader.annotations.original_text_mentions[annotator]
        for note_id, labeled_texts in mentions.items():
            for label_text in labeled_texts:
                for label in sorted(label_text.labels, key=str.casefold):
                    if label in reader.annotations.labels:
                        table.add_row(annotator, str(note_id), label_text.text, label)

    if args.csv:
        cli_utils.print_table_as_csv(table)
    else:
        rich.get_console().print(table)
        console_utils.print_ignored_charts(reader)
