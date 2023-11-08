from collections.abc import Iterable
from enum import EnumMeta
import re
from chart_review import common, config
from chart_review.common import guard_str, guard_iter


def merge_simple(source: dict, append: dict) -> dict:
    """
    TODO: refactor JSON manipulation to labelstudio.py
    @param source: SOURCE of LabelStudio "note" ID mappings
    @param append: INHERIT LabelStudio "note" ID mappings
    @return:
    """
    merged = {"files": {}, "annotations": {}}

    for file_id, note_id in source["files"].items():
        merged["files"][file_id] = int(note_id)
        merged["annotations"][int(note_id)] = source["annotations"][int(note_id)]

        if file_id not in append["files"]:
            continue
        append_id = append["files"][file_id]
        for annotator in append["annotations"][append_id]:
            for entry in append["annotations"][append_id][annotator]:
                if annotator not in merged["annotations"][int(note_id)].keys():
                    merged["annotations"][int(note_id)][annotator] = list()
                if entry.get("labels"):
                    merged["annotations"][int(note_id)][annotator].append(entry)
    return merged


def simplify_full(exported_json: str, annotator_enum: config.AnnotatorMap) -> dict:
    """
    LabelStudio outputs contain more info than needed for IAA and term_freq.

    * PHI raw physician note text is removed *
    TODO: refactor JSON manipulation to labelstudio.py

    :param exported_json: file output from LabelStudio
    :param annotator_enum: dict like {2:annotator1, 6:annotator2}
    :return: dict key= note_id
    """
    simple = {"files": {}, "annotations": {}}
    for entry in common.read_json(exported_json):
        note_id = int(entry.get("id"))
        file_upload = entry.get("file_upload")
        if file_upload:
            file_id = simplify_file_id(file_upload)
            simple["files"][file_id] = int(note_id)
        else:
            simple["files"][note_id] = int(note_id)

        for annot in entry.get("annotations"):
            completed_by = annot.get("completed_by")
            annotator = annotator_enum[completed_by]
            label = []
            for result in annot.get("result"):
                match = result.get("value")
                label.append(match)

            if note_id not in simple["annotations"].keys():
                simple["annotations"][int(note_id)] = dict()

            simple["annotations"][int(note_id)][annotator] = label
    return simple


def simplify_min(exported_json: str, annotator_enum: EnumMeta) -> dict:
    """
    LabelStudio outputs contain more info than needed for IAA and term_freq.

    * PHI raw physician note text is removed *
    TODO: deprecated, this shouldn't be used anymore.
          This was the alternative export format from LabelStudio

    :param exported_json: file output from LabelStudio
    :param annotator_enum: dict like {2:annotator1, 6:annotator2}
    :return: dict key= note_id
    """
    simple = dict()
    for entry in common.read_json(exported_json):
        note_id = int(entry.get("id"))
        annotator = annotator_enum(entry.get("annotator")).name
        label = entry.get("label")

        if not simple.get(note_id):
            simple[note_id] = dict()

        simple[note_id][annotator] = label
    return simple


def simplify_file_id(file_id: str) -> str:
    """
    TODO: deprecate, this is LabelStudio:UUID:i2b2 mapping dance logic

    :param file_id: labelstudio-file_id.json.optional.extension.json
    :return: simple filename like "file_id.json"
    """
    prefix = re.search("-", file_id).start()  # UUID split in LabelStudio
    suffix = re.search(".json", file_id).start()
    root = file_id[prefix + 1 : suffix]
    return f"{root}.json"


def rollup_mentions(simple: dict, annotator: str, note_range: Iterable) -> dict[int, list[str]]:
    """
    :param simple: prepared map of files and annotations
    :param annotator: an annotator name
    :param note_range: collection of LabelStudio document ID
    :return: dict keys=note_id, values=labels
    """
    rollup = dict()

    for note_id, values in simple["annotations"].items():
        if int(note_id) in guard_iter(note_range):
            if values.get(annotator):
                for annot in values[guard_str(annotator)]:
                    if not rollup.get(note_id):
                        rollup[note_id] = list()

                    for symptom in annot["labels"]:
                        if symptom not in rollup[note_id]:
                            rollup[note_id].append(symptom)
    return rollup


def deprecate_filter_note_range(simple: dict, note_range: Iterable) -> dict:
    """
    TODO: deprecate ore refactor, filter by note range.

    @param simple: simplified() dict
    @param note_range: collection of LabelStudio document ID
    @return: dict filtered by note_range
    """
    filtered = {"files": {}, "annotations": {}}
    for file_id, note_id in simple["files"].items():
        if int(note_id) in guard_iter(note_range):
            foo = simple["annotations"][str(note_id)]
            filtered["annotations"][note_id] = foo
            filtered["files"][file_id] = note_id
    return filtered
