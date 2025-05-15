---
title: Accuracy Command
parent: Chart Review
nav_order: 5
# audience: lightly technical folks
# type: how-to
---

# The Accuracy Command

The `accuracy` command will print agreement statistics like F1 scores and confusion matrices
for every label in your project, between two annotators.

Provide two annotator names (the first name will be considered the ground truth) and
your accuracy scores will be printed to the console.

## Example

```shell
$ chart-review accuracy jill jane
Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane
Macro F1: 0.556

F1     Sens  Spec  PPV  NPV   Kappa  TP  FN  TN  FP  Label   
0.667  0.75  0.6   0.6  0.75  0.341  3   1   3   2   *       
0.667  0.5   1.0   1.0  0.5   0.4    1   1   1   0   Cough   
1.0    1.0   1.0   1.0  1.0   1.0    2   0   1   0   Fatigue 
0      0     0     0    0     0      0   0   1   2   Headache
```

## Options

### \-\-verbose

Use this to also print out a table of per-chart/per-label classifications.
This is helpful for investigating where specifically the two annotators agreed or not.

#### Example

```shell
$ chart-review accuracy jill jane --verbose
Comparing 3 charts (1, 3–4)
Truth: jill
Annotator: jane

╭──────────┬──────────┬────────────────╮
│ Chart ID │ Label    │ Classification │
├──────────┼──────────┼────────────────┤
│ 1        │ Cough    │ TP             │
│ 1        │ Fatigue  │ TP             │
│ 1        │ Headache │ FP             │
├──────────┼──────────┼────────────────┤
│ 3        │ Cough    │ TN             │
│ 3        │ Fatigue  │ TN             │
│ 3        │ Headache │ TN             │
├──────────┼──────────┼────────────────┤
│ 4        │ Cough    │ FN             │
│ 4        │ Fatigue  │ TP             │
│ 4        │ Headache │ FP             │
╰──────────┴──────────┴────────────────╯
```

### \-\-csv

Print the accuracy chart in a machine-parseable CSV format.

Can be used with both the default or verbose modes.

#### Examples

```shell
$ chart-review accuracy jill jane --csv
f1,sens,spec,ppv,npv,kappa,tp,fn,tn,fp,label
0.667,0.75,0.6,0.6,0.75,0.341,3,1,3,2,*
0.667,0.5,1.0,1.0,0.5,0.4,1,1,1,0,Cough
1.0,1.0,1.0,1.0,1.0,1.0,2,0,1,0,Fatigue
0,0,0,0,0,0,0,0,1,2,Headache
```

```shell
$ chart-review accuracy jill jane --verbose --csv
chart_id,label,classification
1,Cough,TP
1,Fatigue,TP
1,Headache,FP
3,Cough,TN
3,Fatigue,TN
3,Headache,TN
4,Cough,FN
4,Fatigue,TP
4,Headache,FP
```
