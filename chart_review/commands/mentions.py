import argparse

import rich
import rich.box
import rich.table
import rich.text

from chart_review import cli_utils, console_utils


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
        annotator_mentions = reader.annotations.original_text_mentions[annotator]
        for note_id, labeled_texts in annotator_mentions.items():
            # Gather all combos of text/label (i.e. all mentions) in this note
            note_mentions = set()
            for labeled_text in labeled_texts:
                text = labeled_text.text and labeled_text.text.casefold()
                for label in labeled_text.labels:
                    if label in reader.annotations.labels:
                        note_mentions.add((text, label))

            # Now add each mention to the table
            for note_mention in sorted(note_mentions, key=lambda m: (m[0], m[1].casefold())):
                table.add_row(annotator, str(note_id), note_mention[0], note_mention[1])

    if args.csv:
        cli_utils.print_table_as_csv(table)
    else:
        rich.get_console().print(table)
        console_utils.print_ignored_charts(reader)
