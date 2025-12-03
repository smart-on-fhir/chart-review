"""Various type declarations for better type hinting."""

import dataclasses
import functools


def _split_label(label_str: str) -> tuple[str, str, str]:
    pieces = label_str.split("|", 2)
    while len(pieces) < 3:
        pieces.append("")
    return tuple(piece.strip() for piece in pieces)


@dataclasses.dataclass(frozen=True)
@functools.total_ordering
class Label:
    label: str
    sublabel_name: str = ""  # empty string means "not provided" / "not used"
    sublabel_value: str = ""

    @classmethod
    def parse(cls, label_str: str) -> "Label":
        """
        This parses a label string into a full Label class.

        It interprets '|' characters as delimiters for the label and sublabel name.
        Surrounding whitespace of any part of the label string is ignored.
        """
        return Label(*_split_label(label_str))

    def __post_init__(self):
        if "|" in self.label or "|" in self.sublabel_name:
            raise ValueError("Invalid character found in label name: '|'.")
        if self.sublabel_name and not self.sublabel_value:
            raise ValueError(
                f"Sublabel name but no sublabel value provided: '{self.sublabel_name}'."
            )

    def __str__(self) -> str:
        """Suitable for presenting to user, though it may be long"""
        if self.sublabel_name:
            short_name = self.sublabel_name.removeprefix(f"{self.label} ")
            if not short_name or self.label == self.sublabel_name:
                return f"{self.label} → {self.sublabel_value}"
            else:
                return f"{self.label} → {short_name} → {self.sublabel_value}"
        else:
            return self.label

    def __lt__(self, other) -> bool:
        """Case-insensitive ordering (useful for presentation to user)"""
        left = tuple(x.casefold() for x in dataclasses.astuple(self))
        right = tuple(x.casefold() for x in dataclasses.astuple(other))
        return left < right

    def namespace(self) -> tuple[str, str]:
        """
        Returns an object combining the "namespace" (i.e. "non-value") parts of the label.

        When sublabels are present, it's the label and sublabel, but not the sublabel value.
        When not using a sublabel, it's just empty strings because the label itself is a value in
        the same "namespace" as all other bare labels.

        This is mostly used for detecting when two labels "conflict", meaning they have the same
        namespace but different values. (like when `frequency` detects conflicting labels for the
        same text)
        """
        if self.sublabel_name:
            return self.label, self.sublabel_name
        else:
            return "", ""


# Map of label_studio_user_id: human name
AnnotatorMap = dict[int, str]

LabelSet = set[Label]
NoteSet = set[int]

# Map of label_studio_note_id: {all labels for that note}
# Usually used in the context of a specific annotator's label mentions.
Mentions = dict[int, LabelSet]


class LabelMatcher:
    """
    Class to match a specific label or a class of labels.

    Examples:
        "A|B|C" will match "A|B|C" but not "A|B|D"
        "A|B" will match both "A|B|C" and "A|B|D" but not "A|E"
        "A" will match "A|B|C" and "A|E|F" and "A" but not "X"
    """

    def __init__(self, *expressions: str):
        self._labels = frozenset(_split_label(x) for x in expressions)

    def __eq__(self, other):
        return self._labels == other._labels

    def __hash__(self):
        return hash(self._labels)

    def is_match(self, other: Label) -> bool:
        for label in self._labels:
            if (
                label[0] == other.label
                and (not label[1] or label[1] == other.sublabel_name)
                and (not label[2] or label[2] == other.sublabel_value)
            ):
                return True
        return False

    def matches_in_set(self, other: LabelSet) -> LabelSet:
        return {label for label in other if self.is_match(label)}


# Map of label: {all implied labels}
ImpliedLabels = dict[LabelMatcher, LabelSet]

# Map of group: {all member labels}
GroupedLabels = dict[Label, LabelMatcher]


@dataclasses.dataclass
class LabeledText:
    text: str | None
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
