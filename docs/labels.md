---
title: Labels Command
parent: Chart Review
nav_order: 8
# audience: lightly technical folks
# type: how-to
---

# The Labels Command

The `labels` command prints some statistics on the project labels
and how often each annotator used each label.

## Example

```shell
$ chart-review labels
╭───────────┬──────────┬─────────────╮
│ Annotator │ Label    │ Chart Count │
├───────────┼──────────┼─────────────┤
│ Any       │ Cough    │ 2           │
│ Any       │ Fatigue  │ 3           │
│ Any       │ Headache │ 3           │
├───────────┼──────────┼─────────────┤
│ jane      │ Cough    │ 1           │
│ jane      │ Fatigue  │ 2           │
│ jane      │ Headache │ 2           │
├───────────┼──────────┼─────────────┤
│ jill      │ Cough    │ 2           │
│ jill      │ Fatigue  │ 3           │
│ jill      │ Headache │ 0           │
├───────────┼──────────┼─────────────┤
│ john      │ Cough    │ 1           │
│ john      │ Fatigue  │ 2           │
│ john      │ Headache │ 2           │
╰───────────┴──────────┴─────────────╯
```

## Options

### \-\-csv

Print the labels in a machine-parseable CSV format.

#### Examples
```shell
$ chart-review labels --csv > labels.csv
```

```shell
$ chart-review labels --csv
annotator,label,chart_count
Any,Cough,2
Any,Fatigue,3
Any,Headache,3
jane,Cough,1
jane,Fatigue,2
jane,Headache,2
jill,Cough,2
jill,Fatigue,3
jill,Headache,0
john,Cough,1
john,Fatigue,2
john,Headache,2
```
