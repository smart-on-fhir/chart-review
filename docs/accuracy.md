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
$ chart-review accuracy jane john
accuracy-jane-john:
F1     Sens   Spec   PPV    NPV    TP  FN  TN  FP  Label           
0.929  0.958  0.908  0.901  0.961  91  4   99  10  *               
0.895  0.895  0.938  0.895  0.938  17  2   30  2   cough     
0.815  0.917  0.897  0.733  0.972  11  1   35  4   fever  
0.959  1.0    0.812  0.921  1.0    35  0   13  3   headache   
0.966  0.966  0.955  0.966  0.955  28  1   21  1   stuffy-nose
```

## Options

### `--config=PATH`

Use this to point to a secondary (non-default) config file.
Useful if you have multiple label setups (e.g. one grouped into a binary label and one not).

### `--project-dir=DIR`

Use this to run `chart-review` outside of your project dir.
Config files, external annotations, etc will be looked for in that directory. 

### `--save`

Use this to write a JSON and CSV file to the project directory,
rather than printing to the console.
Useful for passing results around in a machine-parsable format.
