"""Methods for showing config & calculated setup info."""

import rich
import rich.box
import rich.table

from chart_review import cohort, console_utils


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
        chart_table.add_row(
            annotator,
            str(len(notes)),
            console_utils.pretty_note_range(notes),
        )
    console.print(chart_table)
    console.print()

    # Labels
    console.print("Labels:", style="bold")
    if reader.class_labels:
        console.print(", ".join(sorted(reader.class_labels, key=str.casefold)))
    else:
        console.print("None", style="italic", highlight=False)
