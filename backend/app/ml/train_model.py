"""
Machine Learning Training Pipeline for Laboratory Blood Report Extraction.
Trains a high-performance token-level entity extractor to classify parameters,
observed values, units, biological reference intervals, flags, and metadata
with maximum recall and precision on clinical reports and OCR extractions.
"""

import os
import re
import joblib
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

from .dataset_generator import build_synthetic_dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrainBloodReportModel")

MODEL_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODEL_DIR / "blood_report_model.joblib"

COMMON_UNITS = {
    "g/dl", "gm/dl", "mg/dl", "ug/dl", "mcg/dl", "fl", "pg", "%", "percent",
    "/cumm", "cells/cumm", "x10^3/mcl", "10^3/ul", "x10^6/ul", "million/mcl",
    "mil/cumm", "u/l", "iu/l", "uiu/ml", "mmol/l", "umol/l", "ng/ml", "pg/ml",
    "mm/hr", "ml/min/1.73m2", "ml/min", "/mcl", "/ul", "lakh/cumm"
}

COMMON_FLAGS = {
    "low", "l", "lo", "below", "high", "h", "hi", "above", "normal", "n",
    "norm", "within", "range", "ok", "alert", "critical", "abnormal"
}

MEDICAL_STEMS = (
    "hem", "leuk", "thromb", "erythr", "neutr", "lymph", "creat", "chol",
    "bili", "gluc", "plat", "urin", "serum", "fast", "acid", "calc", "sod",
    "potass", "iron", "ferr", "vit", "baso", "eosino", "mono", "glob",
    "albu", "phos", "thyro", "tsh", "bun", "egfr", "esr", "crp", "sgpt",
    "sgot", "alt", "ast", "alp", "pcv", "mcv", "mch", "mchc", "rdw"
)


def is_float_str(s: str) -> bool:
    try:
        float(s.replace(",", "").strip())
        return True
    except ValueError:
        return False


def token_to_features(tokens: list, i: int) -> dict:
    tok, _ = tokens[i]
    tok_lower = tok.lower()
    clean_tok = re.sub(r"[^\w\.\-\<\>\/]", "", tok)

    has_dot = "." in tok
    has_comma = "," in tok
    has_hyphen = ("-" in tok or "–" in tok or "—" in tok)
    is_comp = tok in ["<", ">", "<=", ">=", "≤", "≥"]
    is_unit = tok_lower in COMMON_UNITS or any(tok_lower.endswith(u) for u in ["/dl", "/l", "/ml", "/cumm", "/mcl", "/ul"])
    is_flag = tok_lower in COMMON_FLAGS or tok in ["*", "▲", "▼", "↑", "↓"]
    has_medical_stem = any(tok_lower.startswith(stem) for stem in MEDICAL_STEMS)

    features = {
        "bias": 1.0,
        "tok_lower": tok_lower,
        "length": len(tok),
        "is_digit": tok.isdigit(),
        "is_float": is_float_str(clean_tok),
        "has_dot": has_dot,
        "has_comma": has_comma,
        "has_slash": "/" in tok,
        "has_hyphen": has_hyphen,
        "is_comp": is_comp,
        "is_unit": is_unit,
        "is_flag": is_flag,
        "has_med_stem": has_medical_stem,
        "is_title": tok.istitle(),
        "is_upper": tok.isupper(),
        "has_digit": any(c.isdigit() for c in tok),
        "prefix_2": tok_lower[:2] if len(tok) >= 2 else tok_lower,
        "prefix_3": tok_lower[:3] if len(tok) >= 3 else tok_lower,
        "suffix_2": tok_lower[-2:] if len(tok) >= 2 else tok_lower,
        "suffix_3": tok_lower[-3:] if len(tok) >= 3 else tok_lower,
        "rel_pos": round(i / max(len(tokens) - 1, 1), 2),
        "is_first": i == 0,
        "is_last": i == (len(tokens) - 1),
    }

    # Context: 1 step behind
    if i > 0:
        prev_tok, _ = tokens[i - 1]
        prev_lower = prev_tok.lower()
        prev_clean = re.sub(r"[^\w\.\-\<\>\/]", "", prev_tok)
        features.update({
            "prev_lower": prev_lower,
            "prev_is_digit": prev_tok.isdigit(),
            "prev_is_float": is_float_str(prev_clean),
            "prev_is_comp": prev_tok in ["<", ">", "<=", ">=", "≤", "≥"],
            "prev_is_hyphen": "-" in prev_tok or "–" in prev_tok or "—" in prev_tok,
            "prev_is_unit": prev_lower in COMMON_UNITS,
            "prev_has_digit": any(c.isdigit() for c in prev_tok),
            "prev_is_title": prev_tok.istitle(),
        })
    else:
        features["BOS"] = True

    # Context: 2 steps behind
    if i > 1:
        prev2_tok, _ = tokens[i - 2]
        features["prev2_lower"] = prev2_tok.lower()
        features["prev2_is_float"] = is_float_str(re.sub(r"[^\w\.\-\<\>\/]", "", prev2_tok))

    # Context: 1 step ahead
    if i < len(tokens) - 1:
        next_tok, _ = tokens[i + 1]
        next_lower = next_tok.lower()
        next_clean = re.sub(r"[^\w\.\-\<\>\/]", "", next_tok)
        features.update({
            "next_lower": next_lower,
            "next_is_digit": next_tok.isdigit(),
            "next_is_float": is_float_str(next_clean),
            "next_is_comp": next_tok in ["<", ">", "<=", ">=", "≤", "≥"],
            "next_is_hyphen": "-" in next_tok or "–" in next_tok or "—" in next_tok,
            "next_is_unit": next_lower in COMMON_UNITS,
            "next_has_digit": any(c.isdigit() for c in next_tok),
            "next_is_title": next_tok.istitle(),
        })
    else:
        features["EOS"] = True

    # Context: 2 steps ahead
    if i < len(tokens) - 2:
        next2_tok, _ = tokens[i + 2]
        features["next2_lower"] = next2_tok.lower()
        features["next2_is_float"] = is_float_str(re.sub(r"[^\w\.\-\<\>\/]", "", next2_tok))

    return features


def prepare_dataset(dataset):
    X_dict = []
    y = []

    for sentence in dataset:
        for i in range(len(sentence)):
            feats = token_to_features(sentence, i)
            label = sentence[i][1]
            X_dict.append(feats)
            y.append(label)

    return X_dict, y


def train_and_save_model(num_samples: int = 8000):
    logger.info(f"Generating synthetic clinical report dataset ({num_samples} sequences)...")
    dataset = build_synthetic_dataset(num_samples=num_samples)

    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)

    logger.info("Extracting contextual token features...")
    X_train_dict, y_train = prepare_dataset(train_data)
    X_test_dict, y_test = prepare_dataset(test_data)

    logger.info("Vectorizing features...")
    vec = DictVectorizer(sparse=True)
    X_train = vec.fit_transform(X_train_dict)
    X_test = vec.transform(X_test_dict)

    logger.info(f"Training High-Performance Random Forest on {X_train.shape[0]} tokens with {X_train.shape[1]} features...")
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=32,
        min_samples_split=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    logger.info("Evaluating model on test dataset...")
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, digits=4)

    print("=" * 65)
    print("LAB BLOOD REPORT ML MODEL EVALUATION RESULTS:")
    print(f"Overall Token Accuracy: {accuracy * 100:.2f}%")
    print("-" * 65)
    print(report)
    print("=" * 65)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_payload = {
        "model": clf,
        "vectorizer": vec,
        "accuracy": accuracy,
        "report": report,
        "classes": clf.classes_.tolist(),
        "version": "2.0.0",
    }
    joblib.dump(model_payload, MODEL_PATH)
    logger.info(f"Model successfully saved to {MODEL_PATH}")
    return accuracy, report


if __name__ == "__main__":
    train_and_save_model()
