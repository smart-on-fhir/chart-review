"""Various type declarations for better type hinting."""

import dataclasses
from typing import Optional

# Map of label_studio_user_id: human name
AnnotatorMap = dict[int, str]

LabelSet = set[str]
NoteSet = set[int]

# Map of label_studio_note_id: {all labels for that note}
# Usually used in the context of a specific annotator's label mentions.
Mentions = dict[int, LabelSet]

# Map of label: {all implied labels}
ImpliedLabels = dict[str, LabelSet]

# Map of group: {all member labels}
GroupedLabels = dict[str, LabelSet]


@dataclasses.dataclass
class LabeledText:
    text: Optional[str]
    labels: LabelSet


@dataclasses.dataclass
class ProjectAnnotations:
    labels: LabelSet = dataclasses.field(default_factory=set)

    # annotator_name -> Mentions
    mentions: dict[str, Mentions] = dataclasses.field(default_factory=dict)

    # We usually deal with simplified note-wide labels, but sometimes it's helpful to have
    # the original text-to-label associations available, for term frequency analysis.
    # annotators -> note_id -> list of text/label combos
    original_text_mentions: dict[str, dict[int, list[LabeledText]]] = dataclasses.field(
        default_factory=dict
    )

    def remove(self, chart_id: int):
        # Remove any instance of this chart ID
        for mentions in self.mentions.values():
            if chart_id in mentions:
                del mentions[chart_id]
        for mentions in self.original_text_mentions.values():
            if chart_id in mentions:
                del mentions[chart_id]
