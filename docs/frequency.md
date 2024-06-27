---
title: Frequency Command
parent: Chart Review
nav_order: 6
# audience: lightly technical folks
# type: how-to
---

# The Frequency Command

The `frequency` command prints the number of times a piece of text was labeled
a certain way.

It prints a combined count for all annotators as well as a per-annotator breakdown.

Phrases that been labelled different ways are flagged for attention,
because there might be a mistaken label.

## Example

```shell
$ chart-review frequency
╭───────────┬──────────┬─────────┬───────╮
│ Annotator │ Label    │ Mention │ Count │
├───────────┼──────────┼─────────┼───────┤
│ All       │ Cough    │ achoo   │ 3     │
│ All       │ Cough    │ pain*   │ 1     │
│ All       │ Fatigue  │ sigh*   │ 5     │
│ All       │ Fatigue  │ sleepy  │ 3     │
│ All       │ Fatigue  │ ouch*   │ 2     │
│ All       │ Headache │ pain*   │ 2     │
│ All       │ Headache │ sigh*   │ 1     │
│ All       │ Headache │ ouch*   │ 1     │
├───────────┼──────────┼─────────┼───────┤
│ jane      │ Cough    │ achoo   │ 1     │
│ jane      │ Fatigue  │ sigh*   │ 2     │
│ jane      │ Fatigue  │ sleepy  │ 1     │
│ jane      │ Headache │ sigh*   │ 1     │
│ jane      │ Headache │ pain*   │ 1     │
├───────────┼──────────┼─────────┼───────┤
│ jill      │ Cough    │ pain*   │ 1     │
│ jill      │ Cough    │ achoo   │ 1     │
│ jill      │ Fatigue  │ ouch*   │ 2     │
│ jill      │ Fatigue  │ sleepy  │ 1     │
│ jill      │ Fatigue  │ sigh*   │ 1     │
├───────────┼──────────┼─────────┼───────┤
│ john      │ Cough    │ achoo   │ 1     │
│ john      │ Fatigue  │ sigh*   │ 2     │
│ john      │ Fatigue  │ sleepy  │ 1     │
│ john      │ Headache │ pain*   │ 1     │
│ john      │ Headache │ ouch*   │ 1     │
╰───────────┴──────────┴─────────┴───────╯
  * This text has multiple associated labels.
```

## Options

### \-\-csv

Print the frequencies in a machine-parseable CSV format.

#### Examples
```shell
$ chart-review frequency --csv > frequency.csv
```

```shell
$ chart-review frequency --csv
annotator,label,mention,count
All,Cough,achoo,3
All,Cough,pain,1
All,Fatigue,sigh,5
All,Fatigue,sleepy,3
All,Fatigue,ouch,2
All,Headache,pain,2
All,Headache,sigh,1
All,Headache,ouch,1
jane,Cough,achoo,1
jane,Fatigue,sigh,2
jane,Fatigue,sleepy,1
jane,Headache,sigh,1
jane,Headache,pain,1
jill,Cough,pain,1
jill,Cough,achoo,1
jill,Fatigue,ouch,2
jill,Fatigue,sleepy,1
jill,Fatigue,sigh,1
john,Cough,achoo,1
john,Fatigue,sigh,2
john,Fatigue,sleepy,1
john,Headache,pain,1
john,Headache,ouch,1
```
