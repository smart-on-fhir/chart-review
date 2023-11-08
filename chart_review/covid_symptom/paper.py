from chart_review.covid_symptom import config
from chart_review.covid_symptom.config import Annotator, NoteRange
from chart_review import agree
from chart_review import cohort
from chart_review import common


def table2_accuracy_ctakes(self):
    truth = Annotator.amy
    annotator = Annotator.andy

    study_cohort = cohort.CohortReader()

    andy = study_cohort.confusion_matrix(
        Annotator.andy.name, Annotator.ctakes.name, NoteRange.andy.value
    )
    amy = study_cohort.confusion_matrix(
        Annotator.amy.name, Annotator.ctakes.name, NoteRange.amy.value
    )
    matrix = agree.append_matrix(amy, andy)
    table2 = agree.score_matrix(matrix)

    for label in study_cohort.class_labels:
        andy = study_cohort.confusion_matrix(
            Annotator.andy.name, Annotator.ctakes.name, NoteRange.andy.value, label
        )
        amy = study_cohort.confusion_matrix(
            Annotator.amy.name, Annotator.ctakes.name, NoteRange.amy.value, label
        )
        matrix = agree.append_matrix(amy, andy)
        table2[label] = agree.score_matrix(matrix)

    common.write_json(self.getpath(truth, annotator, "table2_ctakes", "json"), table2)

    common.write_text(
        self.getpath(truth, annotator, "table2_ctakes", "csv"),
        agree.csv_table(table2, study_cohort.class_labels),
    )


def table2_accuracy_icd10(self):
    truth = Annotator.amy
    annotator = Annotator.andy

    andy = self.confusion_matrix(Annotator.andy, Annotator.icd10, NoteRange.andy.value)
    amy = self.confusion_matrix(Annotator.amy, Annotator.icd10, NoteRange.amy.value)
    matrix = agree.append_matrix(amy, andy)
    table2 = agree.score_matrix(matrix)

    common.write_json(self.getpath(truth, annotator, "append_matrix", "json"), matrix)

    for label in self.class_labels:
        andy = self.confusion_matrix(Annotator.andy, Annotator.icd10, NoteRange.andy.value, label)
        amy = self.confusion_matrix(Annotator.amy, Annotator.icd10, NoteRange.amy.value, label)
        matrix = agree.append_matrix(amy, andy)
        table2[label] = agree.score_matrix(matrix)

    common.write_json(self.getpath(truth, annotator, "table2_icd10", "json"), table2)

    common.write_text(
        self.getpath(truth, annotator, "table2_icd10", "csv"),
        agree.csv_table(table2, self.class_labels),
    )


def table3_true_prevalence(self):
    score = common.read_json(config.path("publish_table2_ctakes.amy.andy.json"))
    table3 = [
        "variant_era,covid_symptom,cnt,prevalence_apparent,prevalence_true,sensitivity,specificity"
    ]

    with open(config.PREVALENCE_COVID_POS, "r") as f:
        for line in f.readlines():
            if not line.startswith("variant_era"):
                [variant_era, covid_symptom, cnt, prct] = line.strip().split(",")
                prevelance = 0
                if covid_symptom in score.keys():
                    sensitivity = score[covid_symptom]["Sens"]
                    specificity = score[covid_symptom]["Spec"]
                    prevelance = agree.true_prevalence(
                        float(prct), float(sensitivity), float(specificity)
                    )
                table3.append(
                    f"{variant_era},{covid_symptom},{cnt},{prct},{prevelance},{sensitivity},{specificity}"
                )

    table3 = "\n".join(table3) + "\n"
    filepath = config.path("table3_true_prevalence.csv")
    print(filepath)
    common.write_text(filepath, table3)


def publish_supplement(self):
    # Human
    self.table(Annotator.amy, Annotator.alon, NoteRange.amy_alon.value, "human")
    self.table(Annotator.andy, Annotator.alon, NoteRange.andy_alon.value, "human")

    # NLP
    self.score(Annotator.amy, Annotator.ctakes, NoteRange.amy.value, "nlp")
    self.table(Annotator.andy, Annotator.ctakes, NoteRange.andy.value, "nlp")
    self.table(Annotator.alon, Annotator.ctakes, NoteRange.alon.value, "nlp")

    # ICD10
    icd10_range = set(NoteRange.corpus.value).difference(NoteRange.icd10_missing.value)
    icd10_range_andy = icd10_range.intersection(set(NoteRange.andy.value))
    icd10_range_amy = icd10_range.intersection(set(NoteRange.amy.value))
    icd10_range_alon = icd10_range.intersection(
        set(list(NoteRange.amy_alon.value) + list(NoteRange.andy_alon.value))
    )

    self.table(Annotator.amy, Annotator.icd10, icd10_range_amy, "icd10")
    self.table(Annotator.andy, Annotator.icd10, icd10_range_andy, "icd10")
    self.table(Annotator.alon, Annotator.icd10, icd10_range_alon, "icd10")
    self.table(Annotator.ctakes, Annotator.icd10, icd10_range, "icd10")
