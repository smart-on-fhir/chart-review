from enum import Enum

###############################################################################
# Class labels of suicidality
CLASS_LABELS = ["ideation-present",
                "action-present",
                "ideation-past",
                "action-past"]

PROJECT_DIR = '/opt/labelstudio/suicide-icd10'

###############################################################################
# study-specific LabelStudio "Annotator" users and Labelstudio id "NoteRanges"

class Annotator(Enum):
    """
    LabelStudio annotator (reviewer) ID
    """
    andy = 2
    rena = 3
    alon = 4

class NoteRangeCallibration(Enum):
    """
    LabelStudio list of Note IDs
    """
    corpus = range(351, 371)
    rena = corpus
    andy = corpus
    alon = corpus

class NoteRangePSMAug14(Enum):
    """
    PSM August 14th corpus, 50 notes
    """
    corpus = range(1226, 1277)
    rena = corpus
    andy = corpus

