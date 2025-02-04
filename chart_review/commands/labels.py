import argparse

import rich
import rich.box
import rich.table
import rich.text

from chart_review import cli_utils, console_utils, defines


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.set_defaults(func=print_labels)


def print_labels(args: argparse.Namespace) -> None:
    """Show label information on the console."""
    reader = cli_utils.get_cohort_reader(args)

    # Calculate all label counts for each annotator
    label_names = sorted(reader.class_labels, key=str.casefold)
    label_notes: dict[str, dict[str, defines.NoteSet]] = {}  # annotator -> label -> note IDs
    any_annotator_note_sets: dict[str, defines.NoteSet] = {}
    for annotator, mentions in reader.annotations.mentions.items():
        label_notes[annotator] = {}
        for name in label_names:
            note_ids = {note_id for note_id, labels in mentions.items() if name in labels}
            label_notes[annotator][name] = note_ids
            any_annotator_note_sets.setdefault(name, defines.NoteSet()).update(note_ids)

    label_table = cli_utils.create_table("Annotator", "Label", "Chart Count")

    # First add summary entries, for counts across the union of all annotators
    for name in label_names:
        count = f"{len(any_annotator_note_sets.get(name, {})):,}"
        label_table.add_row(rich.text.Text("Any", style="italic"), name, count)

    # Now do each annotator as their own little boxed section
    for annotator in sorted(label_notes.keys(), key=str.casefold):
        label_table.add_section()
        for name, note_set in label_notes[annotator].items():
            count = str(len(note_set))
            label_table.add_row(annotator, name, count)

    if args.csv:
        cli_utils.print_table_as_csv(label_table)
    else:
        rich.get_console().print(label_table)
        console_utils.print_ignored_charts(reader)
