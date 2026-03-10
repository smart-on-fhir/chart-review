---
title: Disagreements Command
parent: Chart Review
nav_order: 6
# audience: lightly technical folks
# type: how-to
---

# The Disagreements Command

The `disagreements` command will print disagreements for every label in your project,
between two annotators.

Provide two annotator names (the first name will be considered the ground truth) and
the disagreements will be printed to the console.

## Example

```shell
$ chart-review disagreements jill jane
Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane

╭──────────┬──────────┬────────────────╮
│ Chart ID │ Label    │ Classification │
├──────────┼──────────┼────────────────┤
│ 1        │ Headache │ FP             │
├──────────┼──────────┼────────────────┤
│ 4        │ Cough    │ FN             │
│ 4        │ Headache │ FP             │
╰──────────┴──────────┴────────────────╯
```

## Options

### \-\-with-ids

Use this to also print the FHIR and anonymous IDs for all resources represented by a chart.
This is the same information from the `ids` command, but presented in one chart for convenience.

#### Example

```shell
$ chart-review accuracy jill jane --with-ids
Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane

╭──────────┬─────────────────────┬─────────────────────┬──────────┬────────────────╮
│ Chart ID │ FHIR ID             │ Anon ID             │ Label    │ Classification │
├──────────┼─────────────────────┼─────────────────────┼──────────┼────────────────┤
│ 1        │ Encounter/A         │ Encounter/X         │ Headache │ FP             │
│ 1        │ DocumentReference/A │ DocumentReference/X │ Headache │ FP             │
├──────────┼─────────────────────┼─────────────────────┼──────────┼────────────────┤
│ 4        │ Encounter/B         │ Encounter/Y         │ Cough    │ FN             │
│ 4        │ DocumentReference/B │ DocumentReference/Y │ Cough    │ FN             │
│ 4        │ Encounter/B         │ Encounter/Y         │ Headache │ FP             │
│ 4        │ DocumentReference/B │ DocumentReference/Y │ Headache │ FP             │
╰──────────┴─────────────────────┴─────────────────────┴──────────┴────────────────╯
```

### \-\-csv

Print the disagreement chart in a machine-parseable CSV format.

#### Examples

```shell
$ chart-review disagreements jill jane --csv
chart_id,label,classification
1,Headache,FP
4,Cough,FN
4,Headache,FP
```

```shell
$ chart-review disagreements jill jane --with-ids --csv
chart_id,fhir_id,anon_id,label,classification
1,Encounter/A,Encounter/X,Headache,FP
1,DocumentReference/A,DocumentReference/X,Headache,FP
4,Encounter/B,Encounter/Y,Cough,FN
4,DocumentReference/B,DocumentReference/Y,Cough,FN
4,Encounter/B,Encounter/Y,Headache,FP
4,DocumentReference/B,DocumentReference/Y,Headache,FP
```
