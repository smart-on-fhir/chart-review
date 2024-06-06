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

F1     Sens  Spec  PPV  NPV   Kappa  TP  FN  TN  FP  Label   
0.667  0.75  0.6   0.6  0.75  0.341  3   1   3   2   *       
0.667  0.5   1.0   1.0  0.5   0.4    1   1   1   0   Cough   
1.0    1.0   1.0   1.0  1.0   1.0    2   0   1   0   Fatigue 
0      0     0     0    0     0      0   0   1   2   Headache
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
