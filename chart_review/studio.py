"""
Classes that parse Label Studio exports.

Does not know about Chart Review concepts like config files.
Simply parses and exposes Label Studio concepts.
"""

import dataclasses

from chart_review import common, defines, errors


@dataclasses.dataclass(kw_only=True)
class Mention:
    """A piece of text and labels, very similar to LabeledText."""

    text: str | None
    labels: defines.LabelSet

    @staticmethod
    def parse(entry: dict) -> "Mention | None":
        if entry.get("origin") not in {None, "manual"}:
            return None  # avoid counting predictions as human annotators

        value = entry.get("value", {})
        text = value.get("text")
        labels = set(value.get("labels", []))
        return Mention(text=text, labels=labels)


@dataclasses.dataclass(kw_only=True)
class Annotation:
    """All of a single source's mentions"""

    author: int
    mentions: list[Mention] = dataclasses.field(default_factory=list)

    @staticmethod
    def parse(entry: dict) -> "Annotation | None":
        author = entry.get("completed_by")
        if author is None:
            return None  # we don't know who annotated this!

        mentions = [Mention.parse(x) for x in entry.get("result", [])]
        mentions = list(filter(None, mentions))  # parse() returns None if we should skip
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
        annotations = [Annotation.parse(x) for x in entry.get("annotations", [])]
        annotations = list(filter(None, annotations))  # parse() returns None if we should skip

        metadata = entry.get("data", {})
        docref_mappings = metadata.get("docref_mappings", {})
        encounter_id = metadata.get("encounter_id") or metadata.get("enc_id")  # old name
        anon_encounter_id = metadata.get("anon_encounter_id") or metadata.get("anon_id")  # old name

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
