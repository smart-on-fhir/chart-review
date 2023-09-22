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
**EACH STUDY HAS STUDY-SPECIFIC COHORT** 

`config.py` defines study specific variables. 

  * study_folder = `/opt/cumulus/chart-review/studyname`
  * class_labels = `['case', 'control', 'unknown', '...']`
  * Annotators 
  * NoteRanges

Enum **Annotators** maps a SimpleName to LabelStudioUserId
* human subject matter expert _like_ "Rena"
* computer method _like_ "NLP" 
* coded data sources _like_ "ICD10"
  
Enum **NoteRanges** maps a selection of NoteID from the corpus 
* corpus = range(1, end+1)
* annotator1_vs_2 = Iterable
* annotator2_vs_3 = Iterable
* annotator3_vs_1 = Iterable
* annotator3_vs_1 = Iterable

---
**BASE COHORT METHODS**

`cohort.py`
* from chartreview import _labelstudio_, _mentions_, _agree_  

class **Cohort** defines the base class to analyze study cohorts.
  * init(`config.py`)
  
`mentions.py` 
* **rollup**(...) : return _LabelStudioExport_ with 1 "rollup" annotation replacing individual mentions
* other methods are rarely used currently
  * overlaps(...) : test if two mentions overlap (True/False)
  * calc_term_freq(...) : term frequency of highlighted mention text 
  * calc_term_label_confusion : report of exact mentions with 2+ class_labels  

`agree.py` get confusion matrix comparing annotators {truth, reviewer}  
* **confusion_matrix** (truth, reviewer, ...) returns List[TruePos, TrueNeg, FalsePos, FalseNeg]  
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