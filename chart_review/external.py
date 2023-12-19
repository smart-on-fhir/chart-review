"""Match external document references & symptoms to Label Studio data"""

import csv
import os
import sys
from typing import Optional

from chart_review import simplify


def _load_csv_symptoms(filename: str) -> dict[str, list[str]]:
    """
    Loads a csv and returns a list of symptoms per docref.

    CSV format is two columns, where the first is docref id and the second is a single symptom.
    Returns docref_id -> list of symptoms for that ID
    """
    docref_to_symptoms = {}

    with open(filename, "r", newline="", encoding="utf8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip header row
        for row in reader:  # row should be [docref_id, symptom]
            docref_id = row[0]
            symptom_list = docref_to_symptoms.setdefault(docref_id, [])
            if row[1]:  # allow for no labels for a docref (no positive symptoms found)
                symptom_list.append(row[1])

    return docref_to_symptoms


def _docref_id_to_label_studio_id(exported_json: list[dict], docref_id: str) -> Optional[int]:
    """Looks at the metadata in Label Studio and grabs the note ID that holds the provided docref"""
    for row in exported_json:
        mappings = row.get("data", {}).get("docref_mappings", {})
        for key, value in mappings.items():
            # Allow either an anonymous ID or the real ID -- collisions seem very unlikely
            # (i.e. real IDs aren't going to be formatted like our long anonymous ID hash)
            if key == docref_id or value == docref_id:
                return int(row["id"])
    return None


def merge_external(
    simple: dict, exported_json: list[dict], project_dir: str, name: str, config: dict
) -> dict:
    """Loads an external csv file annotator and merges them into an existing simple dict"""
    if filename := config.get("filename"):
        full_filename = os.path.join(project_dir, filename)
        symptom_map = _load_csv_symptoms(full_filename)
    else:
        sys.exit(f"Did not understand config for external annotator '{name}'")

    # Inspect exported json to see if it has the metadata we'll need.
    for row in exported_json:
        if "docref_mappings" not in row.get("data", {}):
            sys.exit(
                f"Your Label Studio export does not include DocRef ID mapping metadata!\n"
                f"Consider re-uploading your notes using Cumulus ETL's chart-review command."
            )
        break  # just inspect one

    # Convert each docref_id into an LS id:
    external_simple = {"files": {}, "annotations": {}}
    for docref_id, symptom_list in symptom_map.items():
        ls_id = _docref_id_to_label_studio_id(exported_json, docref_id)
        if ls_id is None:
            continue

        external_simple["files"][ls_id] = ls_id
        annotation_list = external_simple["annotations"].setdefault(ls_id, {}).setdefault(name, [])
        annotation_list.append({"labels": symptom_list})

    # Merge into existing simple dictionary
    return simplify.merge_simple(simple, external_simple)
