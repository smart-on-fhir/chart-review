"""
Classes that parse Label Studio exports.

Does not know about Chart Review concepts like config files.
Simply parses and exposes Label Studio concepts.

Some of this parsing is a little generous (like allowing missing id, origin, type, or from_name
fields), mostly to accommodate tests without fully detailed input.
(Which, I think is fine - generous parsing is good anyway, and tests with fully specified exports
might make it harder to understand what the test is focusing on.)
"""

import dataclasses

from chart_review import common, defines, errors


@dataclasses.dataclass(kw_only=True)
class Mention:
    """A piece of text and labels, very similar to LabeledText."""

    id: str
    text: str
    labels: defines.LabelSet
    from_name: str

    @staticmethod
    def parse(entry: dict) -> "Mention":
        # Check where we're going to find the labels/tags
        match entry.get("type", "labels").casefold():
            case "labels":
                # Looks like:
                # "value": {
                #   "text": "patient has infection",
                #   "labels": ["Infection"]
                # },
                field = "labels"
            case "choices":
                # Looks like:
                # "value": {
                #   "text": "patient is deceased",
                #   "choices": ["False"]
                # },
                field = "choices"
            case "textarea":
                # Looks like:
                # "value": {
                #   "text": ["free form"],
                # },
                field = "text"
            case _:
                raise ValueError(f"Unrecognized Label Studio result type '{entry.get('type')}'.")

        value = entry.get("value", {})
        text = value.get("text", "") if field != "text" else ""
        labels = set(defines.Label(x) for x in value.get(field, []))
        return Mention(
            id=entry.get("id", ""), text=text, labels=labels, from_name=entry.get("from_name", "")
        )


@dataclasses.dataclass(kw_only=True)
class Annotation:
    """All of a single source's mentions"""

    author: int
    mentions: list[Mention] = dataclasses.field(default_factory=list)

    @staticmethod
    def parse(entry: dict, data_keys: set[str]) -> "Annotation | None":
        author = entry.get("completed_by")
        if author is None:
            return None  # we don't know who annotated this!

        # Labels can be nested - e.g. there might be a toplevel label "Illness" and a sublabel
        # (maybe called "Illness Confirmed?") with a three-way choice of "confirmed", "suspected",
        # and "none of the above".
        # The way that would shows up as a mention in an export is a little odd (to my mind):
        # {
        #   "value": {
        #     "text": "text from note",
        #     "labels": ["Illness"]
        #   },
        #   "id": "HI1y_tlNwu",
        #   "from_name": "label",
        #   "to_name": "text",
        #   "type": "labels",
        # },
        # {
        #   "value": {
        #     "text": "text from note",
        #     "choices": ["confirmed"]
        #   },
        #   "id": "HI1y_tlNwu",
        #   "from_name": "Illness Confirmed?",
        #   "to_name": "text",
        #   "type": "choices",
        # },
        #
        # So you can see there that the "id" field is re-used, and the sublabel refers to the
        # parent via "from_name".

        # When parsing here, we'll first look for the toplevel entries (identifiable by a
        # "from_name" pointing at a key in data_keys). Then do a second pass for any sublabels and
        # adjust the parent with the extra info.
        mentions: list[Mention] = []
        toplevels: dict[str, Mention] = {}
        sublabels: list[Mention] = []
        for result in entry.get("result", []):
            mention = Mention.parse(result)
            if not mention.from_name or mention.from_name in data_keys:
                # This is a toplevel mention
                toplevels[mention.id] = mention
                mentions.append(mention)
            else:
                # It's a sublabel, set it aside for a second
                sublabels.append(mention)

        # Now match up the sublabels
        base_sets: dict[str, defines.LabelSet] = {}
        for sublabel in sublabels:
            if sublabel.id not in toplevels:
                raise ValueError(f"Unrecognized sublabel ID '{sublabel.id}'.")
            toplevel = toplevels[sublabel.id]

            # Wipe out any toplevel tags (existence of a sublabel implies no toplevel labels)
            if toplevel.id not in base_sets:
                base_sets[toplevel.id] = toplevel.labels
                toplevel.labels = set()

            # Now merge in new labels (preserving other fields like `text` from toplevel entry)
            base_labels = base_sets[toplevel.id]
            for label in sublabel.labels:
                for base_label in base_labels:
                    toplevel.labels.add(
                        defines.Label(base_label.label, sublabel.from_name, label.label)
                    )

        return Annotation(author=author, mentions=mentions)


@dataclasses.dataclass(kw_only=True)
class Note:
    """All of a single note's annotations"""

    note_id: int
    annotations: list[Annotation] = dataclasses.field(default_factory=list)

    # metadata
    docref_mappings: dict[str, str] = dataclasses.field(default_factory=dict)
    encounter_id: str | None = None
    anon_encounter_id: str | None = None

    @staticmethod
    def parse(entry: dict) -> "Note":
        metadata = entry.get("data", {})
        docref_mappings = metadata.get("docref_mappings", {})
        encounter_id = metadata.get("encounter_id") or metadata.get("enc_id")  # old name
        anon_encounter_id = metadata.get("anon_encounter_id") or metadata.get("anon_id")  # old name

        data_keys = set(metadata.keys())
        annotations = [
            Annotation.parse(x, data_keys=data_keys) for x in entry.get("annotations", [])
        ]
        annotations = list(filter(None, annotations))  # parse() returns None if we should skip

        return Note(
            note_id=entry["id"],
            annotations=annotations,
            docref_mappings=docref_mappings,
            encounter_id=encounter_id,
            anon_encounter_id=anon_encounter_id,
        )


class ExportFile:
    """Parse information from a single Label Studio export file."""

    def __init__(self, path: str):
        try:
            data = common.read_json(path)
        except Exception as exc:
            errors.exit_for_invalid_project(str(exc))

        self._notes = [Note.parse(x) for x in data]

    @property
    def notes(self) -> list[Note]:
        return self._notes
