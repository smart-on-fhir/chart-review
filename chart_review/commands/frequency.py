import argparse

import rich
import rich.box
import rich.table
import rich.text

from chart_review import cli_utils, console_utils, defines


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.set_defaults(func=print_frequency)


def print_frequency(args: argparse.Namespace) -> None:
    """
    Print counts of each text mention.
    """
    reader = cli_utils.get_cohort_reader(args)

    frequencies = {}  # annotator -> label -> text -> count
    all_annotator_frequencies = {}  # label -> text -> count
    text_labels = {}  # text -> labelset (to flag term confusion)
    for annotator in reader.annotations.original_text_mentions:
        annotator_mentions = reader.annotations.original_text_mentions[annotator]
        for labeled_texts in annotator_mentions.values():
            for labeled_text in labeled_texts:
                text = (labeled_text.text or "").strip().casefold()
                for label in labeled_text.labels:
                    if label in reader.annotations.labels:
                        # Count the mention for this annotator
                        label_to_text = frequencies.setdefault(annotator, {})
                        text_to_count = label_to_text.setdefault(label, {})
                        text_to_count[text] = text_to_count.get(text, 0) + 1

                        # Count the mention for our running all-annotators total
                        all_text_to_count = all_annotator_frequencies.setdefault(label, {})
                        all_text_to_count[text] = all_text_to_count.get(text, 0) + 1

                        # And finally, add it to our running term-confusion tracker
                        text_labels.setdefault(text, defines.LabelSet()).add(label)

    # Now group up the data into a formatted table
    table = cli_utils.create_table("Annotator", "Label", "Mention", "Count")
    has_term_confusion = False  # whether multiple labels are used for the same text

    # Helper method to add all the info for a single annotator to our table
    def add_annotator_to_table(name, label_to_text: dict) -> None:
        nonlocal has_term_confusion
        table.add_section()
        for label in sorted(label_to_text, key=str.casefold):
            text_to_count = label_to_text[label]
            for text, count in sorted(
                text_to_count.items(), key=lambda t: (t[1], t[0]), reverse=True
            ):
                is_confused = not args.csv and text and len(text_labels[text]) > 1
                if is_confused:
                    text = rich.text.Text(text + "*", style="bold")
                    has_term_confusion = True
                table.add_row(name, label, text, f"{count:,}")

    # Add each annotator
    add_annotator_to_table(rich.text.Text("All", style="italic"), all_annotator_frequencies)
    for annotator in sorted(frequencies, key=str.casefold):
        add_annotator_to_table(annotator, frequencies[annotator])

    if args.csv:
        cli_utils.print_table_as_csv(table)
    else:
        rich.get_console().print(table)
        console_utils.print_ignored_charts(reader)
        if has_term_confusion:
            rich.get_console().print(
                "  * This text has multiple associated labels.", style="italic"
            )
