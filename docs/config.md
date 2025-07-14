---
title: Configuration
parent: Chart Review
nav_order: 3
# audience: lightly technical folks
# type: reference
---

# Configuration

## File Format

You can write your config file in either
[JSON](https://en.wikipedia.org/wiki/JSON)
or [YAML](https://en.wikipedia.org/wiki/YAML).
Whichever you're more comfortable with.

By default, Chart Review will look for either `config.json` or `config.yaml`
in your project directory and use whichever it finds.

For the remainder of this document, examples will be shown in YAML.

## Alternative Configs
You may want to experiment with different label setups for your project.
That's easy.

Just provide `--config=./path/to/config.yaml` and your
secondary config will be used instead of the default config.

## Required Fields

All fields have some reasonable default, and thus none are required.
In fact, you can skip using a config file altogether, if the defaults work for you.

But it's strongly recommended to make a config for at least the `annotators` field,
because otherwise you'll be stuck talking about "annotator 1 and 2" instead of "Alice and Bob".

## Field Definitions

### `annotators`

This is a mapping of human-readable names to Label Studio IDs.

Any Label Studio ID not mentioned in this mapping will be ignored.

#### Example

Here, Alice has user ID 3 in Label Studio and Bob has the user ID 2.

```yaml
annotators:
  alice: 3
  bob: 2
```

#### External Annotators

{: .note }
This feature requires you to upload notes
to Label Studio using Cumulus ETL's `upload-notes` command.
That way the document IDs get stored correctly as Label Studio metadata.

Sometimes you are working with externally-derived annotations.
For example, from NLP or ICD10 codes.

That's easy to integrate!
Just make a CSV file with two columns:
first an identifier for the document and second, the label.

- The document identifier can be an Encounter or DocumentReference ID
  (either the original ID or the anonymized version that Cumulus ETL creates).
- The label should be the same kind of label you define in your config.
- An ID can appear multiple times with different labels. All the labels will apply to that note.
- If there are no labels for a given ID, include a line for that ID but with an empty label field.
  That way, Chart Review will know to include that ID in its math, but with no labels.

##### Example CSV
```csv
encounter_id,label
abcd123,Cough
abcd123,Fever
efgh456,
ijkl789,Cough
```

##### Example Config
```yaml
annotators:
  icd10:
    filename: icd10.csv
```

### `grouped-labels`

This lets you bundle certain labels together into a smaller set.
For example, you may have many labels for specific heart conditions, but
are ultimately only interested in the binary determination of whether a patient is affected at all.

This grouping happens after implied labels are expanded and before any scoring is done.

The new group labels do not need to be a part of your source `labels` list.

#### Example
```yaml
grouped-labels:
  animal: [dog, cat, fox]
```

### `ignore`

This lets you totally exclude some notes from annotation scoring.

Sometimes notes were included in the Chart Review but are determined to be invalid for the
purposes of the current study.
If put in this ignore list, they won't affect the score.

You can use either the Label Studio note ID directly,
an Encounter ID (original or anonymized),
or a DocumentReference ID (original or anonymized).

#### Example
```yaml
ignore:
  - abcd123
  - 42
```

### `implied-labels`

This lets you expand certain labels to a fuller set of implied labels.
For example, you may have specific labels like `heart-attack`
that also imply the `heart-condition` label.

This expansion happens before labels are grouped and before any scoring is done.

#### Example

```yaml
implied-labels:
  cat: [animal, has-tail]
  lion: cat
```

### `labels`

This lets you restrict scoring to just this specific set of labels.

Sometimes your source annotations have extra labels that aren't a part of your current analysis.
If a label isn't in this list, it will not be scored.

If this is not defined, all found labels will be used and scored.

#### Example

```yaml
labels:
  - animal
  - cat
  - has-tail
  - lion
```

### `ranges`

This is a mapping of note ranges for each annotator.
By default, note ranges are automatically detected by looking at the Label Studio export.
But it may be useful to manually define the note range in unusual cases.

- You can provide a list of Label Studio note IDs.
- You can reference other defined ranges.
- You can specify a range of IDs with a hyphen.
- Ranges are inclusive. That is, `2-4` includes notes 2, 3, and 4.

#### Example

```yaml
ranges:
  alice: 13-54
  bob: [5, 7, 14]
  cathy: [alice, bob]
```