def score_kappa(truth: list, annotator: list):
    """
    Computes Cohen kappa for pair-wise annotators.
    https://gist.github.com/LouisdeBruijn/1db0283dc69916516e2948f0eefc3a6e#file-cohen_kappa-py

    TODO: refactor This method is NOT actively used, however remains here for comparison.
          (Low priority)

    :param truth: annotations provided by truth annotator
    :param annotator: annotations provided by other annotator
    :rtype: float
    :return: Cohen kappa statistic
    """
    count = 0
    for an1, an2 in zip(truth, annotator):
        if an1 == an2:
            count += 1
    observed = count / len(truth)  # observed agreement A (Po)

    uniq = set(truth + annotator)
    expected = 0  # expected agreement E (Pe)
    for item in uniq:
        cnt1 = truth.count(item)
        cnt2 = annotator.count(item)
        count = (cnt1 / len(truth)) * (cnt2 / len(annotator))
        expected += count

    return round((observed - expected) / (1 - expected), 4)
