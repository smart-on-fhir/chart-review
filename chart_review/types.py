"""Various type declarations for better type hinting."""

# Map of label_studio_user_id: human name
AnnotatorMap = dict[int, str]

# Map of label_studio_note_id: {all labels for that note}
Mentions = dict[int, set[str]]

# Map of label: {all implied labels}
ImpliedLabels = dict[str, set[str]]
