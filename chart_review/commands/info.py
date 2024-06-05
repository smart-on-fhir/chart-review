"""Methods for showing config & calculated setup info."""

import rich
import rich.box
import rich.table

from chart_review import cohort


def info(reader: cohort.CohortReader) -> None:
    """
    Show project information on the console.

    :param reader: the cohort configuration
    """
    console = rich.get_console()

    # Charts
    chart_table = rich.table.Table(
        "Annotator",
        "Chart Count",
        "Chart IDs",
        box=rich.box.ROUNDED,
        pad_edge=False,
        title="Annotations:",
        title_justify="left",
        title_style="bold",
    )
    for annotator in sorted(reader.note_range):
        notes = reader.note_range[annotator]
        chart_table.add_row(annotator, str(len(notes)), pretty_note_range(notes))
    console.print(chart_table)
    console.print()

    # Labels
    console.print("Labels:", style="bold")
    if reader.class_labels:
        console.print(", ".join(sorted(reader.class_labels, key=str.casefold)))
    else:
        console.print("None", style="italic", highlight=False)


def pretty_note_range(notes: set[int]) -> str:
    ranges = []
    range_start = None
    prev_note = None

    def end_range() -> None:
        if prev_note is None:
            return
        if range_start == prev_note:
            ranges.append(str(prev_note))
        else:
            ranges.append(f"{range_start}–{prev_note}")  # en dash

    for note in sorted(notes):
        if prev_note is None or prev_note + 1 != note:
            end_range()
            range_start = note
        prev_note = note

    end_range()

    return ", ".join(ranges)
