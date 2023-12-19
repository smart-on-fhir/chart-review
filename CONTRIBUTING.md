# Contributing to Chart Review

First off, thank you!
Read on below for tips on getting involved with the project.

## Talk to Us

If something annoys you, it probably annoys other folks too.
Don't be afraid to suggest changes or improvements!

Not every suggestion will align with project goals,
but even if not, it can help to talk it out.

Look at [open issues](https://github.com/smart-on-fhir/chart-review/issues),
and if you don't see your concern,
[file a new issue](https://github.com/smart-on-fhir/chart-review/issues/new)!

## Set up your dev environment

To use the same dev environment as us, you'll want to run these commands:
```sh
pip install .[dev]
pre-commit install
```

This will install dependencies & build tools,
as well as set up a `black` auto-formatter commit hook.

## Vocabulary

Here is a quick introduction to some terminology you'll see in the source code.

### Labels
- **Label**: a tag that can be applied to a word, like "Fever" or "Ideation".
  These are often applied by humans during a chart review in Label Studio,
  but external sources like ICD10 codes can also be converted to labels.
  We try to use "label" for the _idea_ of a label (class not instance).
- **Mention**: a specific instance of a label applied to a note.
- **Annotations**: the complete calculated set of mentions across all sources in the project.

### Sources of Labels
- **Annotator**: A generic chart reviewer / labeler.
- **Truth**: The ground truth annotator during an accuracy comparison.
- **External**: An annotator that does not come from Label Studio.
  Usually this means a non-human source like ICD10 codes or NLP.
