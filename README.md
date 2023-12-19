# Chart Review

**Measure agreement between chart annotators.**

Whether your chart annotations come from humans, machine-learning, or coded data like ICD-10,
`chart-review` can compare them to reveal interesting statistics like:

**Accuracy**
* F1-score ([agreement](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1090460/))
* [Sensitivity and Specificity](https://en.wikipedia.org/wiki/Sensitivity_and_specificity)
* [Positive (PPV) or Negative Predictive Value (NPV)](https://en.wikipedia.org/wiki/Positive_and_negative_predictive_values#Relationship)
* False Negative Rate (FNR)

**Confusion Matrix**
* TP = True Positive (type I error)
* TN = True Negative (type II error)
* FP = False Positive
* FN = False Negative

## Documentation

For guides on installing & using Chart Review,
[read our documentation](https://docs.smarthealthit.org/cumulus/chart-review/).

## Example

```shell
$ ls
config.yaml  labelstudio-export.json

$ chart-review accuracy jane john
accuracy-jane-john:
F1     Sens  Spec  PPV  NPV  TP  FN  TN  FP  Label
0.889  0.8   1.0   1.0  0.5  4   1   1   0   *
1.0    1.0   1.0   1.0  1.0  1   0   1   0   Cough
0      0     0     0    0    2   0   0   0   Fatigue
0      0     0     0    0    1   1   0   0   Headache
```

## Contributing

We love 💖 contributions!

If you have a good suggestion 💡 or found a bug 🐛,
[read our brief contributors guide](CONTRIBUTING.md)
for pointers to filing issues and what to expect.
