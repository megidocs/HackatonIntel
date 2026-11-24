"""Reproducible classifier and zero-shot comparison on the same report set."""

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter

import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline

from backend.report_extraction import extract_report
from .reports import LABELS, TEST_REPORTS, training_reports


def fit_classifier():
    labels, reports = zip(*training_reports())
    classifier = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True), LogisticRegression(max_iter=400))
    return classifier.fit(reports, labels)


def metrics(expected, predicted, times):
    labels = [*LABELS, "unresolved"]
    return {
        "accuracy": round(accuracy_score(expected, predicted), 4),
        "macro_f1": round(f1_score(expected, predicted, labels=LABELS, average="macro", zero_division=0), 4),
        "median_ms": round(median(times), 2),
        "labels": labels,
        "matrix": confusion_matrix(expected, predicted, labels=labels).tolist(),
        "unresolved": predicted.count("unresolved"),
    }


def compare(model_url: str | None = None):
    test_labels, reports = zip(*TEST_REPORTS)
    classifier = fit_classifier()
    predicted, times = [], []
    for report in reports:
        started = perf_counter()
        predicted.append(classifier.predict([report])[0])
        times.append((perf_counter() - started) * 1000)
    result = {
        "training_reports": len(training_reports()),
        "test_reports": len(reports),
        "tfidf_logistic_regression": metrics(test_labels, predicted, times),
    }
    if model_url:
        predicted, times = [], []
        errors = 0
        with httpx.Client(timeout=45, trust_env=False) as client:
            for report in reports:
                started = perf_counter()
                try:
                    prediction = extract_report(client, model_url, report).incident_type
                except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
                    prediction = None
                    errors += 1
                predicted.append(prediction or "unresolved")
                times.append((perf_counter() - started) * 1000)
        result["zero_shot_llm"] = {**metrics(test_labels, predicted, times), "invalid_responses": errors}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-url", help="Base URL of the local llama.cpp server.")
    parser.add_argument("--output", type=Path, help="Write a reproducible JSON report.")
    args = parser.parse_args()
    result = json.dumps(compare(args.model_url), indent=2)
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
