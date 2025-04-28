"""Methods for McNemar calculations."""

import argparse
from typing import Optional

import rich
import rich.box
import rich.table
import rich.text
from scipy.stats import binom, chi2

from chart_review import cli_utils, console_utils


def make_subparser(parser: argparse.ArgumentParser) -> None:
    cli_utils.add_project_args(parser)
    cli_utils.add_output_args(parser)
    parser.add_argument("truth_annotator")
    parser.add_argument("annotator1")
    parser.add_argument("annotator2")
    parser.set_defaults(func=print_mcnemar)


def print_mcnemar(args: argparse.Namespace) -> None:
    """
    McNemar calculation between three annotators (one truth, two normal).

    More information:
     https://en.wikipedia.org/wiki/McNemar's_test
     https://pmc.ncbi.nlm.nih.gov/articles/PMC3716987/
    """
    reader = cli_utils.get_cohort_reader(args)
    truth = args.truth_annotator
    annotator1 = args.annotator1
    annotator2 = args.annotator2

    all_people = {truth, annotator1, annotator2}
    annotators = [annotator1, annotator2]

    for annotator in all_people:
        if annotator not in reader.note_range:
            raise ValueError(f"Unrecognized annotator '{annotator}'")

    if len(all_people) != 3:
        raise ValueError("Can’t compare the same annotator with themselves.")

    # Grab the intersection of ranges
    note_range = reader.note_range[truth]
    for annotator in annotators:
        note_range &= reader.note_range[annotator]

    labels = [None, *sorted(reader.class_labels, key=str.casefold)]

    # Calculate contingency tables
    matrices = {
        label: reader.contingency_table(truth, annotator1, annotator2, note_range, label)
        for label in labels
    }

    console = rich.get_console()

    table = cli_utils.create_table(
        "McNemar", "P-value", "BC", "OL", "OR", "BW", "Label", dense=True
    )
    empty_val = "" if args.csv else "N/A"
    for label in labels:
        m = matrices[label]
        mcn, pval = _mcnemar(len(m["OL"]), len(m["OR"]), continuity_correction=True)
        table.add_row(
            empty_val if mcn is None else _small_float(mcn),
            _small_float(pval),
            str(len(m["BC"])),
            str(len(m["OL"])),
            str(len(m["OR"])),
            str(len(m["BW"])),
            label or "*",
        )

    if args.csv:
        cli_utils.print_table_as_csv(table)
        return

    # OK we aren't printing a CSV file to stdout, so we can include a bit more explanation
    # as a little header to the real results.
    note_count = len(note_range)
    chart_word = "chart" if note_count == 1 else "charts"
    pretty_ranges = f" ({console_utils.pretty_note_range(note_range)})" if note_count > 0 else ""
    console.print(f"Comparing {note_count} {chart_word}{pretty_ranges}")
    console.print(f"Truth: {truth}")
    console.print(f"Annotators: {', '.join(annotators)}")
    console.print()

    console.print(table)


def _small_float(number: float) -> str:
    rounded = str(round(number, 3))
    if number == 0 or rounded != "0.0":
        return rounded

    # Too small for simple rounding, use scientific notation instead
    return f"{number:.2e}"


# From https://en.wikipedia.org/wiki/McNemar's_test
# Licensed as CC-BY-SA-4.0
# With small tweaks to fit our style and return the McNemar test value.
def _mcnemar(b: int, c: int, continuity_correction: bool = False) -> tuple[Optional[float], float]:
    n_min, n_max = sorted([b, c])
    corr = 1 if continuity_correction else 0
    if (n_min + n_max) < 25:
        chi2_statistic = None
        pvalue = 2 * binom.cdf(n_min, n_min + n_max, 0.5) - binom.pmf(n_min, n_min + n_max, 0.5)
    else:
        chi2_statistic = (abs(n_min - n_max) - corr) ** 2 / (n_min + n_max)
        pvalue = chi2.sf(chi2_statistic, 1)
    return chi2_statistic, pvalue
