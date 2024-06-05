---
title: Info Command
parent: Chart Review
nav_order: 6
# audience: lightly technical folks
# type: how-to
---

# The Info Command

The `info` command will print information about your current project.

This is helpful to examine the computed list of chart ID ranges or labels.

## Example

```shell
$ chart-review info
Annotations:                              
╭──────────┬─────────────┬──────────╮
│Annotator │ Chart Count │ Chart IDs│
├──────────┼─────────────┼──────────┤
│jane      │ 3           │ 1, 3–4   │
│jill      │ 4           │ 1–4      │
│john      │ 3           │ 1–2, 4   │
╰──────────┴─────────────┴──────────╯

Labels:
Cough, Fatigue, Headache
```

## Options

### `--config=PATH`

Use this to point to a secondary (non-default) config file.
Useful if you have multiple label setups (e.g. one grouped into a binary label and one not).

### `--project-dir=DIR`

Use this to run `chart-review` outside of your project dir.
Config files, external annotations, etc will be looked for in that directory. 
