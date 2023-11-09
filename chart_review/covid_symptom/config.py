from enum import Enum
import ctakesclient
from chart_review import common

###############################################################################
# COVID Symptom Class Labels
#
# ctakesclient.filesystem.covid_symptoms()


CLASS_LABELS = [
    "Congestion or runny nose",
    "Cough",
    "Diarrhea",
    "Dyspnea",
    "Fatigue",
    "Fever or chills",
    "Headache",
    "Loss of taste or smell",
    "Muscle or body aches",
    "Nausea or vomiting",
    "Sore throat",
]

###############################################################################
# Export directory and LabelStudio JSON files

PROJECT_DIR = "/opt/labelstudio/covid"

###############################################################################
#
# study-specific LabelStudio "Annotator" users and Labelstudio id "NoteRanges"


class Annotator(Enum):
    """
    LabelStudio annotator (reviewer) ID
    """

    andy = 2
    amy = 3
    alon = 6
    ctakes = 7  # mcmurry.andy
    icd10 = 0


class NoteRange(Enum):
    """
    LabelStudio list of ED Notes
    """

    corpus = range(782, 1006)
    amy = range(782, 895)
    andy = range(895, 1006)
    andy_alon = range(979, 1006)
    amy_alon = range(864, 891)
    alon = set(range(864, 891)).union(set(range(979, 1006)))
    icd10_missing = [
        782,
        791,
        793,
        799,
        811,
        824,
        826,
        828,
        833,
        837,
        859,
        860,
        870,
        877,
        882,
        886,
        921,
        959,
        985,
        986,
        994,
        1004,
    ]
