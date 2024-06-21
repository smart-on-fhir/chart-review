---
title: Labels Command
parent: Chart Review
nav_order: 7
# audience: lightly technical folks
# type: how-to
---

# The Labels Command

The `labels` prints some statistics on the project labels
and how often each annotator used each label.

## Example

```shell
$ chart-review labels
╭───────────┬─────────────┬──────────╮
│ Annotator │ Chart Count │ Label    │
├───────────┼─────────────┼──────────┤
│ Any       │ 2           │ Cough    │
│ Any       │ 3           │ Fatigue  │
│ Any       │ 3           │ Headache │
├───────────┼─────────────┼──────────┤
│ jane      │ 1           │ Cough    │
│ jane      │ 2           │ Fatigue  │
│ jane      │ 2           │ Headache │
├───────────┼─────────────┼──────────┤
│ jill      │ 2           │ Cough    │
│ jill      │ 3           │ Fatigue  │
│ jill      │ 0           │ Headache │
├───────────┼─────────────┼──────────┤
│ john      │ 1           │ Cough    │
│ john      │ 2           │ Fatigue  │
│ john      │ 2           │ Headache │
╰───────────┴─────────────┴──────────╯
```
