# chart-review
Measure agreement between two "_reviewers_" from the "_confusion matrix_"

**Accuracy**
* F1-score ([agreement](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1090460/))
* [Sensitivity and Specificity](https://en.wikipedia.org/wiki/Sensitivity_and_specificity)
* [Positive (PPV) or Negative Predictive Value (NPV)](https://en.wikipedia.org/wiki/Positive_and_negative_predictive_values#Relationship))
* False Negative Rate (FNR) 

**Confusion Matrix** 
* TP = True Positive (type I error)
* TN = True Negative (type II error)
* FP = False Positive 
* FN = False Negative 

**Power Calculations** for sample size estimation
* Power = 1 - FNR 
* FNR = FN / (FN + TP) 


---
**CHART-REVIEW** here is defined as "reading" and "annotating" (highlighting) medical notes to measure accuracy of a measurement.
Measurements can establish the reliability of ICD10, or the reliable utility of NLP to automate labor intensive process. 
 
Agreement among 2+ human subject matter expert reviewers is considered the defacto gold-standard for ground-truth labeling, but cannot be done manually at scale.  

The most common chart-review measures agreement of the _**class_label**_ from a careful list of notes 
* 1 human reviewer _vs_ ICD10 codes
* 1 human reviewer _vs_ NLP results
* 2 human reviewers _vs_ each other

---
### How to Install
1. Clone this repo.
2. Install it locally like so: `pipx install .`

`chart-review` is not yet released on PyPI.

---
### How to Run

#### Set Up Project Folder

Chart Review operates on a project folder that holds your config & data.
1. Make a new folder.
2. Export your Label Studio annotations and put that in the folder as `labelstudio-export.json`.
3. Add a `config.yaml` file (or `config.json`) that looks something like this (read more on this format below):

```yaml
labels:
  - cough
  - fever

annotators:
  jane: 2
  john: 6
  jack: 8

ranges:
  jane: 242-250  # inclusive
  john: [260-271, 277]
  jack: [jane, john]
```

#### Run

Call `chart-review` with the sub-command you want and its arguments:

For Jane as truth for Jack's annotations:
```shell
chart-review accuracy jane jack
```

For Jack as truth for John's annotations:
```shell
chart-review accuracy jack john
```

Pass `--help` to see more options.

---
### Config File Format 

`config.yaml` defines study specific variables. 

  * Class labels: `labels: ['cough', 'fever']`
  * Annotators: `annotators: {'jane': 3, 'john': 8}`
  * Note ranges: `ranges: {'jane': 40-50, 'john': [2, 3, 4, 5]}`

`annotators` maps a name to a Label Studio User ID
* human subject matter expert _like_ `jane`
* computer method _like_ `nlp` 
* coded data sources _like_ `icd10`
  
`ranges` maps a selection of Note IDs from the corpus 
* `corpus: start:end`
* `annotator1_vs_2: [list, of, notes]`
* `annotator2_vs_3: corpus`

#### External Annotations

You may have annotations from NLP or coded FHIR data that you want to compare against.
Easy!

Set up your config to point at a CSV file in your project folder that holds two columns:
- DocRef ID (real or anonymous)
- Label

```yaml
annotators:
  human: 1
  external_nlp:
    filename: my_nlp.csv
```

When `chart-review` runs, it will inject the external annotations and match up the DocRef IDs
to Label Studio notes based on metadata in your Label Studio export.

---
**BASE COHORT METHODS**

`cohort.py`
* from chart_review import _labelstudio_, _mentions_, _agree_

class **Cohort** defines the base class to analyze study cohorts.
  * init(`config.py`)
  
`simplify.py`
* **rollup**(...) : return _LabelStudioExport_ with 1 "rollup" annotation replacing individual mentions

`term_freq.py` (methods are rarely used currently)
* overlaps(...) : test if two mentions overlap (True/False)
* calc_term_freq(...) : term frequency of highlighted mention text
* calc_term_label_confusion : report of exact mentions with 2+ class_labels

`agree.py` get confusion matrix comparing annotators {truth, annotator}
* **confusion_matrix** (truth, annotator, ...) returns List[TruePos, TrueNeg, FalsePos, FalseNeg]
* **score_matrix** (matrix) returns dict with keys {F1, Sens, Spec, PPV, NPV, TP,FP,TN,FN}

`labelstudio.py` handles LabelStudio JSON

Class **LabelStudioExport**
* init(`labelstudio-export.json`)

Class **LabelStudioNote**
* init(...)

`publish.py` tables and figures for PubMed manuscripts 
* table_csv(...)
* table_json(...)

---
**NICE TO HAVES LATER**

* **_confusion matrix_** type support using Pandas
* **score_matrix** would be nicer to use a Pandas strongly typed class

---
### Set up your dev environment

To use the same dev environment as us, you'll want to run these commands:
```sh
pip install .[dev]
pre-commit install
```
