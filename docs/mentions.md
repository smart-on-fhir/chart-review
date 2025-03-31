---
title: Mentions Command
parent: Chart Review
nav_order: 10
# audience: lightly technical folks
# type: how-to
---

# The Mentions Command

The `mentions` command prints each time a piece of text was labeled
and with what label.

## Example

```shell
$ chart-review mentions
╭───────────┬──────────┬─────────┬──────────╮
│ Annotator │ Chart ID │ Mention │ Label    │
├───────────┼──────────┼─────────┼──────────┤
│ jane      │ 1        │ achoo   │ Cough    │
│ jane      │ 1        │ sigh    │ Headache │
│ jane      │ 1        │ sigh    │ Fatigue  │
│ jane      │ 4        │ sleepy  │ Fatigue  │
│ jane      │ 4        │ pain    │ Headache │
├───────────┼──────────┼─────────┼──────────┤
│ jill      │ 1        │ achoo   │ Cough    │
│ jill      │ 1        │ sigh    │ Fatigue  │
│ jill      │ 2        │ ouch    │ Fatigue  │
│ jill      │ 4        │ sleepy  │ Fatigue  │
│ jill      │ 4        │ pain    │ Cough    │
├───────────┼──────────┼─────────┼──────────┤
│ john      │ 1        │ achoo   │ Cough    │
│ john      │ 1        │ sigh    │ Fatigue  │
│ john      │ 2        │ ouch    │ Headache │
│ john      │ 4        │ sleepy  │ Fatigue  │
│ john      │ 4        │ pain    │ Headache │
╰───────────┴──────────┴─────────┴──────────╯
```

## Options

### \-\-csv

Print the mentions in a machine-parseable CSV format.

#### Examples
```shell
$ chart-review mentions --csv > mentions.csv
```

```shell
$ chart-review mentions --csv
annotator,chart_id,mention,label
jane,1,achoo,Cough
jane,1,sigh,Headache
jane,1,sigh,Fatigue
jane,4,sleepy,Fatigue
jane,4,pain,Headache
jill,1,achoo,Cough
jill,1,sigh,Fatigue
jill,2,ouch,Fatigue
jill,4,sleepy,Fatigue
jill,4,pain,Cough
john,1,achoo,Cough
john,1,sigh,Fatigue
john,2,ouch,Headache
john,4,sleepy,Fatigue
john,4,pain,Headache
```
