---
title: Chart Review
has_children: true
# audience: non-programmers new to this project
# type: explanation
---

# Chart Review

**Measure agreement between chart reviewers.**

Whether your chart annotations come from humans, machine-learning, or coded data like ICD-10,
Chart Review can compare them to reveal interesting statistics like:

**Accuracy**
* [F1-score](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1090460/) (agreement)
* [Cohen's Kappa](https://en.wikipedia.org/wiki/Cohen's_kappa) (agreement)
* [Sensitivity and Specificity](https://en.wikipedia.org/wiki/Sensitivity_and_specificity)
* [Positive (PPV) or Negative Predictive Value (NPV)](https://en.wikipedia.org/wiki/Positive_and_negative_predictive_values#Relationship)
* False Negative Rate (FNR)

**Confusion Matrix**
* TP = True Positive (type I error)
* TN = True Negative (type II error)
* FP = False Positive
* FN = False Negative

**Power Calculations** for sample size estimation
* Power = 1 - FNR
* FNR = FN / (FN + TP)

## Is This Part of Cumulus?

Chart Review is developed by the same team
and is designed to work with the
[Cumulus project](https://docs.smarthealthit.org/cumulus/),
but Chart Review is useful even outside of Cumulus.

Some features (notably those dealing with external annotations)
require Label Studio metadata that Cumulus ETL creates when it pushes notes
to Label Studio using its `upload-notes` feature.

But calculating accuracy between human annotators can be done entirely without the use of Cumulus.

## Installing & Using

```shell
pipx install chart-review
chart-review --help
```

Read the [first-time setup docs](setup.md) for more.

## Example

```shell
$ chart-review
╭───────────┬─────────────┬───────────╮
│ Annotator │ Chart Count │ Chart IDs │
├───────────┼─────────────┼───────────┤
│ jane      │ 3           │ 1, 3–4    │
│ jill      │ 4           │ 1–4       │
│ john      │ 3           │ 1–2, 4    │
╰───────────┴─────────────┴───────────╯

Pass --help to see more options.
```

## Source Code
Chart Review is open source.
If you'd like to browse its code or contribute changes yourself,
the code is on [GitHub](https://github.com/smart-on-fhir/chart-review).
