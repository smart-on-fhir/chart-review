## Vocabulary

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
