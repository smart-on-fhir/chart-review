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
import os
import sys

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
            case "choices":
                # Looks like:
                # "value": {
                #   "text": "patient is deceased",
                #   "choices": ["False"]
                # },
                field = "choices"
                is_list = True
            case "datetime":
                # Looks like:
                # "value": {
                #   "text": "Nov 15",
                #   "datetime": "2018-11-15",
                # },
                field = "datetime"
                is_list = False
            case "labels":
                # Looks like:
                # "value": {
                #   "text": "patient has infection",
                #   "labels": ["Infection"]
                # },
                field = "labels"
                is_list = True
            case "textarea":
                # Looks like:
                # "value": {
                #   "text": ["free form"],
                # },
                field = "text"
                is_list = True
            case _:
                raise ValueError(f"Unrecognized Label Studio result type '{entry.get('type')}'.")

        value = entry.get("value", {})
        text = value.get("text", "") if field != "text" else ""
        field_value = value.get(field)
        if not field_value:
            labels = set()
        elif is_list:
            labels = {defines.Label(x) for x in field_value}
        else:
            labels = {defines.Label(field_value)}
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

        # When parsing here, we'll first look for the toplevel entries (the first use of any given
        # "id" value). Then do a second pass for any sublabels and adjust the parent with the extra
        # info.
        mentions: list[Mention] = []
        toplevels: dict[str, Mention] = {}
        sublabels: list[Mention] = []
        for result in entry.get("result", []):
            mention = Mention.parse(result)
            if not mention.id or mention.id not in toplevels:
                # This is a toplevel mention
                toplevels[mention.id] = mention
                mentions.append(mention)
            else:
                # It's a sublabel, set it aside for a second
                sublabels.append(mention)

        # Now match up the sublabels
        base_sets: dict[str, defines.LabelSet] = {}
        for sublabel in sublabels:
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
    def _prefix_note(note_ref: str) -> str:
        # For historical reasons, prefix DocRef/ if we're dealing with an ID not a Ref
        return note_ref if "/" in note_ref else f"DocumentReference/{note_ref}"

    @staticmethod
    def parse(entry: dict) -> "Note":
        metadata = entry.get("data", {})
        docref_mappings = metadata.get("docref_mappings", {})
        encounter_id = metadata.get("encounter_id") or metadata.get("enc_id")  # old name
        anon_encounter_id = metadata.get("anon_encounter_id") or metadata.get("anon_id")  # old name

        # Normalize mappings
        docref_mappings = {
            Note._prefix_note(key): Note._prefix_note(val) for key, val in docref_mappings.items()
        }

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
    """Parse information from Label Studio export files."""

    def __init__(self, path: str):
        """If path is a file, load it. If a folder, merge all export files in it."""
        self._notes = []
        note_hashes = {}

        if os.path.isdir(path):
            filenames = sorted(
                os.path.join(path, name)
                for name in os.listdir(path)
                if name.casefold().endswith(".json")
            )
        else:
            filenames = [path]

        for name in filenames:
            try:
                data = common.read_json(name)
            except Exception as exc:
                print(f"Could not parse '{name}': {exc}", file=sys.stderr)
                continue

            # Confirm it is (very roughly) shaped like an LS export.
            # We are pretty loose, for unit testing's sake.
            # If we end up reading files we shouldn't in the real world, we can add a few more
            # keys to check for.
            if not data or not isinstance(data, list):
                continue
            if not isinstance(data[0], dict):
                continue
            if "id" not in data[0]:
                continue

            # Fold new notes into running list
            new_notes = [Note.parse(x) for x in data]
            for note in new_notes:
                if note.docref_mappings:
                    # Smush the note IDs together to form a stable string
                    ids_hash = hash(tuple(sorted(note.docref_mappings.items())))
                    if old_note := note_hashes.get(ids_hash):
                        self._merge_notes(old_note, note)
                    else:
                        note_hashes[ids_hash] = note
                        self._notes.append(note)
                else:
                    self._notes.append(note)

        if not self._notes:
            errors.exit_for_invalid_project("No Label Studio export data found.")

    @staticmethod
    def _merge_notes(old: Note, new: Note) -> None:
        # Only merge annotations, take all the metadata from the old note
        for new_annot in new.annotations:
            for old_annot in old.annotations:
                if old_annot.author == new_annot.author:
                    old_annot.mentions.extend(new_annot.mentions)
                    break
            else:
                old.annotations.append(new_annot)
                continue

    @property
    def notes(self) -> list[Note]:
        return self._notes
