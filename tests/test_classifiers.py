from classifiers.rule_based import classify as rule_classify
from classifiers.ml_based import classify as ml_classify

def test_rule_based():
    assert rule_classify("Invoice details") == "invoice"
    assert rule_classify("Other document") == "other"

def test_ml_based():
    assert ml_classify("Total amount") == "ml-invoice"
    assert ml_classify("Nothing here") == "ml-other"
