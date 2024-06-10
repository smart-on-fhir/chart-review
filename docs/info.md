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
╭──────────┬─────────────┬──────────╮
│Annotator │ Chart Count │ Chart IDs│
├──────────┼─────────────┼──────────┤
│jane      │ 3           │ 1, 3–4   │
│jill      │ 4           │ 1–4      │
│john      │ 3           │ 1–2, 4   │
╰──────────┴─────────────┴──────────╯
```

## Options

### `--ids`

Prints a mapping of chart & FHIR IDs to the console, in CSV format.
Redirect the output to a file to save it to disk.

This is helpful when you are juggling anonymous IDs from Cumulus's Athena database
as well as original IDs from your EHR, on top of the Label Studio chart IDs.

{: .note }
FHIR IDs could be considered PHI depending on how the EHR generates them.
Exercise appropriate caution when sharing the output of this command.

#### Examples

```shell
$ chart-review info --ids > ids.csv
```

```shell
$ chart-review info --ids
chart_id,original_fhir_id,anonymized_fhir_id
1,Encounter/E123,Encounter/170a37476339af6f31ed7b1b0bbb4f11d5daacd79bf9f490d49f93742acfd2bd
1,DocumentReference/D123,DocumentReference/331ab320fe6264535a408aa1a7ecf1465fc0631580af5f3010bfecf71c99d141
2,Encounter/E898,Encounter/8b0bd207147989492801b7c14eebc015564ab73a07bdabdf9aefc3425eeba982
2,DocumentReference/D898,DocumentReference/b5e329b752067eca1584f9cd132f40c637d8a9ebd6f2a599794f9436fb83c2eb
2,DocumentReference/D899,DocumentReference/605338cd18c2617864db23fd5fd956f3e806af2021ffa6d11c34cac998eb3b6d
```

### `--labels`

Prints some statistics on the project labels and how often each annotator used each label.

#### Example

```shell
$ chart-review info --labels
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

### `--config=PATH`

Use this to point to a secondary (non-default) config file.
Useful if you have multiple label setups (e.g. one grouped into a binary label and one not).

### `--project-dir=DIR`

Use this to run `chart-review` outside of your project dir.
Config files, external annotations, etc will be looked for in that directory. 
