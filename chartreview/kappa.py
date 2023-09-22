def score_kappa(gold_ann: list, review_ann: list):
    """
    TODO: refactor This method is NOT actively used, however remains here for comparison. (Low priority)

    Computes Cohen kappa for pair-wise annotators.
    https://gist.github.com/LouisdeBruijn/1db0283dc69916516e2948f0eefc3a6e#file-cohen_kappa-py

    :param gold_ann: annotations provided by first annotator
    :type gold_ann: list
    :param review_ann: annotations provided by second annotator
    :type review_ann: list
    :rtype: float
    :return: Cohen kappa statistic
    """
    count = 0
    for an1, an2 in zip(gold_ann, review_ann):
        if an1 == an2:
            count += 1
    observed = count / len(gold_ann)  # observed agreement A (Po)

    uniq = set(gold_ann + review_ann)
    expected = 0  # expected agreement E (Pe)
    for item in uniq:
        cnt1 = gold_ann.count(item)
        cnt2 = review_ann.count(item)
        count = ((cnt1 / len(gold_ann)) * (cnt2 / len(review_ann)))
        expected += count

    return round((observed - expected) / (1 - expected), 4)
