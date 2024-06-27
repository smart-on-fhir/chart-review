---
title: IDs Command
parent: Chart Review
nav_order: 7
# audience: lightly technical folks
# type: how-to
---

# The IDs Command

The `ids` command prints a mapping of chart & FHIR IDs to the console, in CSV format.
Redirect the output to a file to save it to disk.

This is helpful when you are juggling anonymous IDs from Cumulus's Athena database
as well as original IDs from your EHR, on top of the Label Studio chart IDs.

{: .note }
FHIR IDs could be considered PHI depending on how the EHR generates them.
Exercise appropriate caution when sharing the output of this command.

## Example

<!--
For the examples in this doc, you can use this as your labelstudio-export.json file:
[
  {
    "id": 1,
    "data": {
      "enc_id": "E123",
      "anon_id": "170a37476339af6f31ed7b1b0bbb4f11d5daacd79bf9f490d49f93742acfd2bd",
      "docref_mappings": {
        "D123": "331ab320fe6264535a408aa1a7ecf1465fc0631580af5f3010bfecf71c99d141"
      }
    }
  },
  {
    "id": 2,
    "data": {
      "enc_id": "E898",
      "anon_id": "8b0bd207147989492801b7c14eebc015564ab73a07bdabdf9aefc3425eeba982",
      "docref_mappings": {
        "D898": "b5e329b752067eca1584f9cd132f40c637d8a9ebd6f2a599794f9436fb83c2eb",
        "D899": "605338cd18c2617864db23fd5fd956f3e806af2021ffa6d11c34cac998eb3b6d"
      }
    }
  }
]
-->

```shell
$ chart-review ids
╭──────────┬────────────────────────┬──────────────────────────────────────────╮
│ Chart ID │ Original FHIR ID       │ Anonymized FHIR ID                       │
├──────────┼────────────────────────┼──────────────────────────────────────────┤
│ 1        │ Encounter/E123         │ Encounter/170a37476339af6f31ed7b1b0bbb4f │
│          │                        │ 11d5daacd79bf9f490d49f93742acfd2bd       │
│ 1        │ DocumentReference/D123 │ DocumentReference/331ab320fe6264535a408a │
│          │                        │ a1a7ecf1465fc0631580af5f3010bfecf71c99d1 │
│          │                        │ 41                                       │
│ 2        │ Encounter/E898         │ Encounter/8b0bd207147989492801b7c14eebc0 │
│          │                        │ 15564ab73a07bdabdf9aefc3425eeba982       │
│ 2        │ DocumentReference/D898 │ DocumentReference/b5e329b752067eca1584f9 │
│          │                        │ cd132f40c637d8a9ebd6f2a599794f9436fb83c2 │
│          │                        │ eb                                       │
│ 2        │ DocumentReference/D899 │ DocumentReference/605338cd18c2617864db23 │
│          │                        │ fd5fd956f3e806af2021ffa6d11c34cac998eb3b │
│          │                        │ 6d                                       │
╰──────────┴────────────────────────┴──────────────────────────────────────────╯
```

## Options

### \-\-csv

Print the IDs in a machine-parseable CSV format.

Because IDs can be quite long, this is also probably the best approach for searching
for a given ID, since line wraps won't appear in the middle of your ID.

#### Examples
```shell
$ chart-review ids --csv > ids.csv
```

```shell
$ chart-review ids --csv
chart_id,original_fhir_id,anonymized_fhir_id
1,Encounter/E123,Encounter/170a37476339af6f31ed7b1b0bbb4f11d5daacd79bf9f490d49f93742acfd2bd
1,DocumentReference/D123,DocumentReference/331ab320fe6264535a408aa1a7ecf1465fc0631580af5f3010bfecf71c99d141
2,Encounter/E898,Encounter/8b0bd207147989492801b7c14eebc015564ab73a07bdabdf9aefc3425eeba982
2,DocumentReference/D898,DocumentReference/b5e329b752067eca1584f9cd132f40c637d8a9ebd6f2a599794f9436fb83c2eb
2,DocumentReference/D899,DocumentReference/605338cd18c2617864db23fd5fd956f3e806af2021ffa6d11c34cac998eb3b6d
```
