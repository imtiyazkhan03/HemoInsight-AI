"""
Inference Engine for Trained Laboratory Blood Report Entity Extraction Model.
Converts extracted raw text and OCR lines into structured BloodTestItem objects
with high accuracy across laboratory parameters, biological reference ranges, units, and flags.
"""

import os
import re
import uuid
import json
import joblib
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .train_model import token_to_features, is_float_str
from ..models.schemas import BloodTestItem, ReportMetadata, ExtractionConfidence, TestStatus

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).resolve().parent / "models" / "blood_report_model.joblib"
KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "reference_ranges.json"


class MLInferenceEngine:
    _instance = None

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.accuracy = 0.0
        self.classes = []
        self.is_loaded = False
        self.knowledge = {}
        self.load_knowledge()
        self.load_model()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_knowledge(self):
        if KNOWLEDGE_PATH.exists():
            try:
                with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load reference ranges in ML engine: {e}")

    def find_canonical_match(self, name: str) -> Tuple[Optional[str], Optional[dict]]:
        if not name or not self.knowledge:
            return None, None
        clean = name.strip().lower()
        clean = re.sub(r"[\(\)\[\]\{\}\:\,\-\/\.]", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()

        # Exact key match
        if clean in self.knowledge:
            return clean, self.knowledge[clean]

        # Alias match
        for key, data in self.knowledge.items():
            for alias in data.get("aliases", []):
                norm_alias = alias.lower().strip()
                norm_alias = re.sub(r"[\(\)\[\]\{\}\:\,\-\/\.]", " ", norm_alias)
                norm_alias = re.sub(r"\s+", " ", norm_alias).strip()
                if clean == norm_alias or norm_alias in clean or clean in norm_alias:
                    return key, data

        return None, None

    def load_model(self):
        if MODEL_PATH.exists():
            try:
                payload = joblib.load(MODEL_PATH)
                self.model = payload.get("model")
                self.vectorizer = payload.get("vectorizer")
                self.accuracy = payload.get("accuracy", 0.0)
                self.classes = payload.get("classes", [])
                self.is_loaded = True
                logger.info(f"Loaded trained blood report ML model (accuracy: {self.accuracy:.4f})")
            except Exception as e:
                logger.error(f"Failed to load ML model from {MODEL_PATH}: {e}")
                self.is_loaded = False
        else:
            logger.warning(f"ML model file not found at {MODEL_PATH}")
            self.is_loaded = False

    def normalize_ocr_line(self, line: str) -> str:
        """
        Cleans common OCR errors, splits glued numbers and units, and heals fragmented words.
        """
        cleaned = line.strip()
        # Fix OCR typos in flags
        cleaned = re.sub(r"\bNORl?MAL\b", "NORMAL", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bHlGH\b", "HIGH", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bL0W\b", "LOW", cleaned, flags=re.IGNORECASE)

        # Fix common OCR word fragmentations
        cleaned = re.sub(r"\bHe\s+moglobin\b", "Hemoglobin", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bCe\s+ll\b", "Cell", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bPlate\s+lets\b", "Platelets", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bDiag\s+nostic\b", "Diagnostic", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bPatie\s+nt\b", "Patient", cleaned, flags=re.IGNORECASE)

        # Split glued unit and numbers: e.g. "mg/dL0.6" -> "mg/dL 0.6"
        cleaned = re.sub(r"([a-zA-Z%]+)(\d)", r"\1 \2", cleaned)
        cleaned = re.sub(r"(\d)([a-zA-Z%]+)", r"\1 \2", cleaned)

        # Standardize hyphens between numbers: "12.0-16.0" -> "12.0 - 16.0"
        cleaned = re.sub(r"(\d)\s*[-–—]\s*(\d)", r"\1 - \2", cleaned)

        return cleaned

    def tokenize_line(self, line: str) -> List[str]:
        cleaned = self.normalize_ocr_line(line)
        tokens = []
        raw_toks = cleaned.split()
        for tok in raw_toks:
            # Handle cases like "(12.0-16.0)" while keeping units like mg/dL intact
            sub_toks = re.findall(r"[A-Za-z0-9\.\<\>\%\^\-\–\—\:\/]+|[\(\)\[\]\|\,]", tok)
            if sub_toks:
                tokens.extend(sub_toks)
            else:
                tokens.append(tok)
        return tokens

    def parse_range(self, range_tokens: List[str]) -> Tuple[Optional[float], Optional[float], str]:
        range_text = " ".join(range_tokens)
        cleaned = range_text.replace("–", "-").replace("—", "-").replace("to", "-").replace(",", ".").strip()

        # Format: < 200 or <= 200
        lt_match = re.search(r"[<≤]\s*([0-9]+\.?[0-9]*)", cleaned)
        if lt_match:
            try:
                return 0.0, float(lt_match.group(1)), range_text
            except ValueError:
                pass

        # Format: > 40 or >= 40
        gt_match = re.search(r"[>≥]\s*([0-9]+\.?[0-9]*)", cleaned)
        if gt_match:
            try:
                return float(gt_match.group(1)), 999999.0, range_text
            except ValueError:
                pass

        # Format: min - max
        range_match = re.search(r"([0-9]+\.?[0-9]*)\s*-\s*([0-9]+\.?[0-9]*)", cleaned)
        if range_match:
            try:
                return float(range_match.group(1)), float(range_match.group(2)), range_text
            except ValueError:
                pass

        return None, None, range_text

    def extract_from_lines(self, lines: List[str]) -> Tuple[ReportMetadata, List[BloodTestItem]]:
        """
        Runs ML model token classification line by line and groups entities into blood test items.
        """
        items: List[BloodTestItem] = []
        patient_name = None
        collection_date = None
        lab_name = None

        if not self.is_loaded or self.model is None or self.vectorizer is None:
            logger.warning("ML model is not loaded. Falling back.")
            return ReportMetadata(filename="unknown", file_type="Unknown"), []

        for line_idx, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 4:
                continue

            # Check header metadata
            lower = line_clean.lower()
            if any(term in lower for term in ["patient", "name:", "pt. name", "client", "customer"]) and not patient_name:
                p_match = re.search(r"(?:patient\s*(?:name)?|name|pt\.?\s*name)\s*[:\-]?\s*([A-Za-z\.\s]+?)(?=\s+(?:age|sex|gender|date|id|yrs|years|\d|\()|$)", line_clean, re.I)
                if p_match:
                    patient_name = p_match.group(1).strip()
            if "date" in lower and not collection_date:
                d_match = re.search(r"(?:date|collected|time)\s*[:\-]?\s*([0-9]{1,2}[-\/][A-Za-z0-9]{2,4}[-\/][0-9]{2,4}|[A-Za-z]{3}\s+[0-9]{1,2},?\s+[0-9]{4})", line_clean, re.I)
                if d_match:
                    collection_date = d_match.group(1).strip()
            if any(w in lower for w in ["lab", "hospital", "clinic", "diagnostic", "pathology"]) and not lab_name:
                lab_name = line_clean

            # Skip lines that are purely patient, doctor, hospital, or address metadata
            if re.search(r"\b(?:patient|doctor|referred|phone|mobile|tel|address|suite|ave|street|uhid|mrn|barcode|bill|receipt|reg\s*no|page\s*\d+|signature|authorized)\b", lower):
                continue
            if re.search(r"\b(?:name|age|sex|gender|dob|y\/o|yrs?|years?|male|female)\s*[:\-]", lower):
                continue

            # Tokenize and predict
            tokens = self.tokenize_line(line_clean)
            if len(tokens) < 2:
                continue

            # Build feature dictionaries
            dummy_sentence = [(t, "O") for t in tokens]
            feat_dicts = [token_to_features(dummy_sentence, i) for i in range(len(tokens))]
            X = self.vectorizer.transform(feat_dicts)
            predictions = self.model.predict(X)

            # Group predicted tokens
            param_tokens = []
            val_tokens = []
            unit_tokens = []
            range_tokens = []
            flag_tokens = []

            for tok, label in zip(tokens, predictions):
                if label in ["B-PARAM", "I-PARAM"]:
                    param_tokens.append(tok)
                elif label == "VALUE":
                    val_tokens.append(tok)
                elif label == "UNIT":
                    unit_tokens.append(tok)
                elif label == "REF_RANGE":
                    range_tokens.append(tok)
                elif label == "FLAG":
                    flag_tokens.append(tok)

            # A valid laboratory parameter line requires at least a parameter name and a value
            if param_tokens and val_tokens:
                raw_name = " ".join(param_tokens).strip(":,|- ")
                val_raw = val_tokens[0].strip(":,|- ")

                # Skip demographic or person names falsely caught by ML
                name_lower = raw_name.lower()
                if patient_name and (patient_name.lower() in name_lower or name_lower in patient_name.lower()):
                    continue
                if re.search(r"^(?:mr|mrs|ms|miss|master|baby|dr|prof|shri|smt)\b", name_lower):
                    continue
                non_lab = {"patient", "doctor", "report", "test name", "investigation", "observed value", "units", "name", "age", "sex", "gender", "male", "female", "years", "yrs", "hospital", "clinic", "diagnostic", "address", "phone", "mobile", "suite", "ave", "street", "uhid", "mrn", "barcode"}
                name_words = set(re.findall(r"[a-z]+", name_lower))
                if name_words.intersection(non_lab):
                    continue

                parsed_val = None
                try:
                    clean_v = val_raw.replace(",", ".")
                    parsed_val = float(re.sub(r"[^\d\.]", "", clean_v))
                except (ValueError, TypeError):
                    pass

                unit_str = " ".join(unit_tokens).strip(":,|- ") if unit_tokens else None
                ref_min, ref_max, ref_text = self.parse_range(range_tokens)
                flag_str = " ".join(flag_tokens).strip(":,|- ") if flag_tokens else None

                # Canonical reference match fallback
                canon_key, canon_data = self.find_canonical_match(raw_name)
                display_name = raw_name
                category = "General Laboratory"
                desc = None
                questions = []

                if canon_data:
                    display_name = canon_data.get("display_name", raw_name)
                    category = canon_data.get("category", category)
                    desc = canon_data.get("description")
                    questions = canon_data.get("questions_for_doctor", [])
                    if not unit_str and canon_data.get("unit"):
                        unit_str = canon_data.get("unit")
                    if (ref_min is None or ref_max is None) and canon_data.get("default_range"):
                        ref_min, ref_max = canon_data["default_range"][0], canon_data["default_range"][1]
                        ref_text = f"{ref_min} - {ref_max}"

                # Determine confidence
                confidence = ExtractionConfidence.HIGH
                needs_verification = False
                verification_reason = None

                if parsed_val is None:
                    confidence = ExtractionConfidence.LOW
                    needs_verification = True
                    verification_reason = "Observed value could not be parsed as a number."
                elif ref_min is None and ref_max is None:
                    confidence = ExtractionConfidence.MEDIUM
                    needs_verification = True
                    verification_reason = "Biological reference interval was not detected in this line."

                item = BloodTestItem(
                    id=str(uuid.uuid4())[:8],
                    test_name=display_name,
                    raw_name=raw_name,
                    category=category,
                    value=parsed_val,
                    raw_value=val_raw,
                    unit=unit_str,
                    ref_min=ref_min,
                    ref_max=ref_max,
                    ref_range_text=ref_text if ref_text else None,
                    lab_flag=flag_str,
                    status=TestStatus.NEEDS_REVIEW,
                    confidence=confidence,
                    needs_verification=needs_verification,
                    verification_reason=verification_reason,
                    description=desc,
                    questions_for_doctor=questions,
                )
                items.append(item)

        metadata = ReportMetadata(
            filename="clinical_report",
            file_type="Document",
            patient_name=patient_name,
            collection_date=collection_date,
            lab_name=lab_name,
        )
        return metadata, items
