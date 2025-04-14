---
title: McNemar Command
parent: Chart Review
nav_order: 9
# audience: lightly technical folks
# type: how-to
---

# The McNemar Command

The `mcnemar` command will print McNemar's test values and associated statistics like
P-value and contingency tables for every label in your project,
between two annotators and a third truth annotator.

Provide three annotator names (the first name will be considered the ground truth) and
your McNemar test values will be printed to the console.

For more details on what McNemar's test is, see its
[Wikipedia article](https://en.wikipedia.org/wiki/McNemar's_test)
and the linked papers there.

## McNemar Variations

There are several variations of McNemar's test.
We use the standard asymptotic test with continuity correction.
When sample sizes are small (`b + c < 25`), we instead use the mid-P version
(which does not actually provide a McNemar test chi-squared value, just a P-value).

## Example

```shell
$ chart-review mcnemar alice bob carla
Comparing 50 charts (1–50)
Truth: alice
Annotators: bob, carla

McNemar  P-value   BC  OL  OR  BW  Label
12.375   4.35e-04  20  61  27  42  *    
6.5      0.011     10  20  6   14  A    
N/A      0.035     1   16  6   27  B    
2.025    0.155     9   25  15  1   C    
```

(The columns BC, OL, OR, and BW mean "both correct", "only left correct", "only right correct",
and "both wrong.")

## Options

### \-\-csv

Print the chart in a machine-parseable CSV format.

#### Example

```shell
$ chart-review mcnemar alice bob carla --csv
mcnemar,p-value,bc,ol,or,bw,label
12.375,4.35e-04,20,61,27,42,*
6.5,0.011,10,20,6,14,A
,0.035,1,16,6,27,B
2.025,0.155,9,25,15,1,C
```
