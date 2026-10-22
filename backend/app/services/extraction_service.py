import io
import re
import json
import uuid
import difflib
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
from ..models.schemas import BloodTestItem, ReportMetadata, ExtractionConfidence, TestStatus
from ..ml.model_inference import MLInferenceEngine

logger = logging.getLogger(__name__)

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "reference_ranges.json"

UNIT_PATTERNS = [
    r"(?:x|X)?10\s*[\^\*\~\-]?\s*[369]\s*\/\s*(?:mcL|uL|cumm|c\.mm|cu\.mm|mm3|L)",
    r"(?:x|X)?10\s*[\^\*\~\-]?\s*12\s*\/\s*L",
    r"10\s*[\^\*\~\-]\s*[369]",
    r"million\/mcL", r"million\/cumm", r"mil\/mcL", r"Mil\/cu\.mm", r"mil\/cu\.mm",
    r"Thous\/cu\.mm", r"thous\/cu\.mm", r"Cells\/cu\.mm", r"cells\/cu\.mm",
    r"cells\/cumm", r"cells\/mcL", r"\/mcL", r"\/uL", r"\/cumm",
    r"g\/dL", r"gm\/dL", r"mg\/dL", r"ug\/dL", r"mcg\/dL",
    r"fL", r"fl", r"pg", r"\%", r"Percent", r"percent", r"U\/L", r"IU\/L", r"uIU\/mL", r"mEq\/L",
    r"mmol\/L", r"umol\/L", r"ng\/mL", r"ng\/dL", r"pg\/mL",
    r"mm\/hr", r"mL\/min\/1\.73m2", r"mL\/min"
]
UNIT_REGEX = r"(?:" + "|".join(UNIT_PATTERNS) + r")"


DEMOGRAPHIC_LINE_PATTERNS = [
    r"\b(?:patient(?:\s*name)?|pt\.?\s*name|client(?:\s*name)?|customer(?:\s*name)?)\s*[:\-]",
    r"\b(?:name|age|sex|gender|dob|y\/o|yrs?|years?|male|female)\s*[:\-]",
    r"\b(?:referred\s*by|ref(?:\s*by|\.)?|consultant|doctor|dr\.)\s*[:\-]",
    r"\b(?:collected\s*(?:on|date)?|reported\s*(?:on|date)?|specimen|sample\s*(?:type)?)\s*[:\-]",
    r"\b(?:hospital|diagnostic|clinic|pathology|laboratory|healthcare|medical\s*center|medical\s*centre|health\s*center)\b",
    r"\b(?:address|suite|ave|avenue|street|road|phone|mobile|tel|fax|email|website|www\.)\b",
    r"\b(?:page\s*\d+|sheet\s*\d+|authorized\s*by|signature|technician|pathologist)\b",
    r"\b(?:barcode|uhid|mrn|ipd|opd|bill\s*no|receipt|invoice|reg(?:\s*no)?|account\s*no|acc\s*no)\s*[:\-]"
]

NON_LAB_WORDS = {
    "patient", "pt", "name", "age", "sex", "gender", "years", "yrs", "male", "female",
    "doctor", "dr", "ref", "referred", "hospital", "clinic", "diagnostic", "laboratory",
    "address", "suite", "ave", "street", "phone", "mobile", "tel", "specimen", "sample",
    "barcode", "uhid", "mrn", "bill", "invoice", "receipt", "reg", "authorized", "signature",
    "page", "ward", "bed", "technician", "pathologist", "consultant", "center", "centre",
    "medical", "healthcare", "foundation", "institute", "dept", "department", "physician",
    "provider", "accession", "account", "order", "doe", "john", "jane", "smith"
}


def normalize_lab_name(text: str) -> str:
    """
    Normalizes a laboratory test name by converting to lowercase, removing extraneous
    punctuation, and standardizing whitespace while keeping alphanumerics.
    """
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[\(\)\[\]\{\}\:\,\-\/\.]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


class ExtractionService:
    def __init__(self):
        self.knowledge = {}
        self.exact_map = {}
        self.sorted_aliases = []
        self.ml_engine = MLInferenceEngine.get_instance()
        self.load_knowledge()

    def is_demographic_line(self, line: str) -> bool:
        lower = line.lower().strip()
        for pat in DEMOGRAPHIC_LINE_PATTERNS:
            if re.search(pat, lower):
                return True
        # Check for medical center / hospital / clinic facility patterns
        if re.search(r"\b(?:medical\s*center|medical\s*centre|health\s*center|diagnostic\s*center)\b", lower):
            return True
        # Check for lines containing multiple date patterns (e.g. "12/20/99 12/20/99 12/22")
        dates = re.findall(r"\b\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?\b", line)
        if len(dates) >= 2:
            return True
        return False

    def is_invalid_test_name(self, name: str, patient_name: Optional[str] = None) -> bool:
        clean = name.strip()
        lower = clean.lower()

        if patient_name:
            p_lower = patient_name.strip().lower()
            if p_lower and (p_lower == lower or p_lower in lower or lower in p_lower):
                return True

        # Check for titles: Dr., Mr., Mrs., etc.
        if re.search(r"^(?:mr|mrs|ms|miss|master|baby|dr|prof|shri|smt)\b", lower):
            return True

        # Check for non-lab words (facility, patient metadata, administrative terms)
        words = set(re.findall(r"[a-z]+", lower))
        if words.intersection(NON_LAB_WORDS):
            return True

        # Check for dates inside the candidate test name (e.g. "DOE JOHN 12/20/99 12/20/99 12/22")
        if re.search(r"\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}", clean):
            return True

        # Check for phone numbers or long digit sequences (e.g. "MEDICAL CENTER 78987654")
        if re.search(r"\b\d{5,}\b", clean):
            return True

        return False

    def load_knowledge(self):
        if KNOWLEDGE_PATH.exists():
            try:
                with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
                self._build_index()
            except Exception as e:
                logger.error(f"Failed to load reference knowledge: {e}")

    def _build_index(self):
        self.exact_map = {}
        self.sorted_aliases = []

        for key, data in self.knowledge.items():
            norm_key = normalize_lab_name(key)
            self.exact_map[norm_key] = (key, data)
            self.sorted_aliases.append((norm_key, key, data))

            for alias in data.get("aliases", []):
                norm_alias = normalize_lab_name(alias)
                if norm_alias:
                    self.exact_map[norm_alias] = (key, data)
                    self.sorted_aliases.append((norm_alias, key, data))

        # Sort aliases by word count and length descending so longer/more specific phrases match first
        self.sorted_aliases.sort(key=lambda x: (len(x[0].split()), len(x[0])), reverse=True)

    def find_canonical_match(self, raw_name: str) -> Tuple[Optional[str], Optional[dict]]:
        """
        Multi-tier canonical parameter matching:
        1. Exact lookup
        2. Prioritized word-boundary matching (longest/most specific aliases first)
        3. Significant token subset matching
        4. High-confidence fuzzy string matching for OCR typos
        """
        if not raw_name or not str(raw_name).strip():
            return None, None

        clean = normalize_lab_name(str(raw_name))
        if not clean:
            return None, None

        # Tier 1: Exact Match
        if clean in self.exact_map:
            return self.exact_map[clean]

        words = clean.split()

        # Tier 2: Word Boundary Match (ordered by specificity)
        for alias, key, data in self.sorted_aliases:
            if len(alias) <= 2:
                # 1-2 letter acronyms (e.g. hb, cr, na, k) must match as an isolated token
                if alias in words:
                    return key, data
                continue

            # Word boundary regex ensuring the alias matches whole words
            pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
            if re.search(pattern, clean):
                return key, data

        # Tier 3: Significant token subset matching
        clean_tokens = set(words)
        stop_words = {"serum", "blood", "total", "count", "test", "level", "examination", "rate", "index", "fraction", "value", "automated", "manual"}
        sig_clean = clean_tokens - stop_words

        if sig_clean:
            best_score = 0.0
            best_match = None
            for alias, key, data in self.sorted_aliases:
                alias_tokens = set(alias.split()) - stop_words
                if not alias_tokens:
                    continue
                if alias_tokens.issubset(sig_clean):
                    score = len(alias_tokens) / len(sig_clean)
                    if score > best_score and score >= 0.5:
                        best_score = score
                        best_match = (key, data)
            if best_match:
                return best_match

        # Tier 4: Fuzzy Match for OCR character corruptions (e.g. "Herrioglobin" -> "hemoglobin")
        if len(clean) >= 4:
            for alias, key, data in self.sorted_aliases:
                if abs(len(clean) - len(alias)) <= 3 and len(alias) >= 4:
                    ratio = difflib.SequenceMatcher(None, clean, alias).ratio()
                    if ratio >= 0.78:
                        return key, data

        return None, None

    def parse_reference_range(self, range_str: str) -> Tuple[Optional[float], Optional[float]]:
        if not range_str or not isinstance(range_str, str):
            return None, None

        cleaned = range_str.replace("–", "-").replace("—", "-").replace("to", "-").strip()

        # Format: < 200 or <= 200
        lt_match = re.search(r"[<≤]\s*([0-9]+\.?[0-9]*)", cleaned)
        if lt_match:
            try:
                return 0.0, float(lt_match.group(1))
            except ValueError:
                pass

        # Format: > 40 or >= 40
        gt_match = re.search(r"[>≥]\s*([0-9]+\.?[0-9]*)", cleaned)
        if gt_match:
            try:
                return float(gt_match.group(1)), 999999.0
            except ValueError:
                pass

        # Format: min - max
        range_match = re.search(r"([0-9]+\.?[0-9]*)\s*-\s*([0-9]+\.?[0-9]*)", cleaned)
        if range_match:
            try:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                return min_val, max_val
            except ValueError:
                pass

        return None, None

    def parse_lab_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parses a single text/OCR line into test name, observed value, unit, reference range, and flag.
        """
        clean = line.strip()
        if not clean or len(clean) < 4:
            return None

        if self.is_demographic_line(clean):
            return None

        lower = clean.lower()
        if any(h in lower for h in [
            "patient name", "report date", "collection date", "referred by", "doctor",
            "lab director", "signature", "page ", "specimen", "investigation observed",
            "test name observed", "parameter observed", "methodology", "biological reference"
        ]):
            return None

        # Strip leading numbers: "1. ", "02) ", "3 - "
        clean = re.sub(r"^\s*\d+[\.\)\-\:\s]+\s*", "", clean)

        # Standardize glued symbols e.g. "10.4g/dL" -> "10.4 g/dL"
        clean = re.sub(r"(\d)([a-zA-Z%])", r"\1 \2", clean)
        clean = re.sub(r"([a-zA-Z%])(\d)", r"\1 \2", clean)
        clean = re.sub(r"[\.]{2,}", " ", clean)
        clean = re.sub(r"[\_]{2,}", " ", clean)

        # 1. Detect Flag at the end of the line
        flag = None
        flag_match = re.search(r"(?:\b(CRITICAL|ALERT|HIGH|HI|LOW|LO|NORMAL|NORM|ABNORMAL)\b|([▲▼↑↓HLN]))\s*$", clean, re.IGNORECASE)
        if flag_match:
            raw_f = flag_match.group(0).upper().strip()
            if raw_f in ["L", "LO", "LOW", "▼", "↓"]:
                flag = "LOW"
            elif raw_f in ["H", "HI", "HIGH", "▲", "↑"]:
                flag = "HIGH"
            elif raw_f in ["NORMAL", "NORM", "N"]:
                flag = "NORMAL"
            elif raw_f in ["CRITICAL", "ALERT"]:
                flag = "CRITICAL"
            clean = clean[:flag_match.start()].strip()

        # 2. Detect Reference Range
        ref_min = None
        ref_max = None
        ref_text = None

        range_match = re.search(r"([\[\(]?\s*(?:[<≤>≥]\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?\s*(?:[-–—to~]+)\s*\d+(?:\.\d+)?)\s*[\]\)]?)(?:\s*$|\s*[A-Za-z])", clean)
        if range_match:
            cand_range = range_match.group(1).strip("()[]")
            ref_text = cand_range.strip()
            if "<" in cand_range or "≤" in cand_range:
                m = re.search(r"\d+(?:\.\d+)?", cand_range)
                if m:
                    ref_min, ref_max = 0.0, float(m.group(0))
            elif ">" in cand_range or "≥" in cand_range:
                m = re.search(r"\d+(?:\.\d+)?", cand_range)
                if m:
                    ref_min, ref_max = float(m.group(0)), 999999.0
            else:
                nums = re.findall(r"\d+(?:\.\d+)?", cand_range)
                if len(nums) >= 2:
                    ref_min, ref_max = float(nums[0]), float(nums[1])

        # 3. Detect Unit
        unit = None
        unit_match = re.search(UNIT_REGEX, clean, re.IGNORECASE)
        if unit_match:
            unit = unit_match.group(0).strip()

        # 4. Extract Observed Value and Test Name
        scrubbed = clean
        if ref_text and range_match:
            scrubbed = scrubbed[:range_match.start()] + " " + scrubbed[range_match.end():]
        if unit:
            scrubbed = re.sub(re.escape(unit), " ", scrubbed, flags=re.IGNORECASE)

        scrubbed = re.sub(r"[\:\|\[\]\(\)\{\}]", " ", scrubbed)
        scrubbed = re.sub(r"\s+", " ", scrubbed).strip()

        num_matches = list(re.finditer(r"\b\d+(?:\.\d+)?\b", scrubbed))
        if not num_matches:
            return None

        val_match = num_matches[-1]
        val = float(val_match.group(0))
        raw_val = val_match.group(0)

        raw_test_name = scrubbed[:val_match.start()].strip()
        raw_test_name = re.sub(r"[\:\-\.\,\/]+$", "", raw_test_name).strip()

        if not raw_test_name or len(raw_test_name) < 2:
            return None

        if self.is_invalid_test_name(raw_test_name):
            return None

        canon_key, canon_data = self.find_canonical_match(raw_test_name)

        # STRICT VALIDATION:
        # A valid laboratory test line must satisfy AT LEAST ONE of:
        # 1. Matches a known laboratory test in the medical knowledge base
        # 2. Has an explicit recognized clinical unit
        # 3. Has an explicit laboratory reference range
        if not canon_data and not unit and not ref_text:
            return None

        return {
            "test_name": raw_test_name,
            "value": val,
            "raw_value": raw_val,
            "unit": unit,
            "ref_min": ref_min,
            "ref_max": ref_max,
            "ref_range_text": ref_text,
            "lab_flag": flag
        }

    def _extract_metadata_from_text(self, text: str, filename: str, file_type: str) -> ReportMetadata:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        patient_name = None
        date_str = None
        lab_name = None

        for line in lines[:35]:
            p_match = re.search(r"(?:Patient Name|Patient|Pt\.?\s*Name|Name)\s*[:\-]\s*([A-Za-z\s\.\,\-]+)", line, re.IGNORECASE)
            if p_match and not patient_name:
                cand = p_match.group(1).strip()
                if len(cand) > 2 and len(cand) < 40 and not any(w in cand.lower() for w in ["test", "report", "date", "age", "sex", "parameter"]):
                    patient_name = cand

            # Match uppercase names like "DOE, JOHN" or "DOE JOHN"
            if not patient_name:
                name_cand = re.search(r"\b([A-Z]{2,}\s*,\s*[A-Z]{2,}|[A-Z]{3,}\s+[A-Z]{3,})\b", line)
                if name_cand and not any(w in name_cand.group(1).lower() for w in ["medical", "center", "clinic", "hospital", "laboratory", "complete", "blood", "count", "panel", "report"]):
                    patient_name = name_cand.group(1).strip()

            d_match = re.search(r"(?:Date|Collection Date|Report Date|Dated|DOB)\s*[:\-]?\s*([0-9]{1,4}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4}|[0-9]{1,2}-[A-Za-z]{3}-[0-9]{2,4})", line, re.IGNORECASE)
            if d_match and not date_str:
                date_str = d_match.group(1).strip()

            l_match = re.search(r"(?:Laboratory|Diagnostic|Hospital|Pathology|Clinic|Medical\s*Center|Health\s*Center)\s*[:\-]?\s*([A-Za-z0-9\s\.\,\-]+)", line, re.IGNORECASE)
            if l_match and not lab_name:
                cand = l_match.group(0).strip()
                if len(cand) > 3 and len(cand) < 60:
                    lab_name = cand
            elif any(w in line.lower() for w in ["medical center", "diagnostic center", "health center"]) and not lab_name:
                lab_name = line.strip()

        return ReportMetadata(
            filename=filename,
            file_type=file_type,
            patient_name=patient_name,
            collection_date=date_str,
            lab_name=lab_name,
        )

    def extract_from_tables(self, tables: List[List[List[str]]], filename: str, file_type: str = "PDF", header_text: str = "") -> Tuple[ReportMetadata, List[BloodTestItem]]:
        """
        Extract blood test items from structured PDF tables extracted by PyMuPDF find_tables().
        """
        metadata = self._extract_metadata_from_text(header_text, filename, file_type)
        items: List[BloodTestItem] = []

        for table in tables:
            if not table or len(table) < 2:
                continue

            header = [str(cell).strip().lower() if cell is not None else "" for cell in table[0]]
            col_test = -1
            col_val = -1
            col_unit = -1
            col_range = -1
            col_flag = -1

            for idx, col_name in enumerate(header):
                if any(w in col_name for w in ["test", "parameter", "investigation", "analyte"]):
                    col_test = idx
                elif any(w in col_name for w in ["value", "result", "observed", "reading"]):
                    col_val = idx
                elif any(w in col_name for w in ["unit"]):
                    col_unit = idx
                elif any(w in col_name for w in ["reference", "range", "interval", "biological", "normal"]):
                    col_range = idx
                elif any(w in col_name for w in ["flag", "status"]):
                    col_flag = idx

            if col_test == -1 and len(header) >= 1:
                col_test = 0
            if col_val == -1 and len(header) >= 2:
                col_val = 1
            if col_unit == -1 and len(header) >= 3:
                col_unit = 2
            if col_range == -1 and len(header) >= 4:
                col_range = 3
            if col_flag == -1 and len(header) >= 5:
                col_flag = 4

            for row in table[1:]:
                if not row or len(row) <= col_test:
                    continue
                raw_test = str(row[col_test]).strip() if row[col_test] is not None else ""
                if not raw_test or any(w in raw_test.lower() for w in ["page", "authorized", "disclaimer", "methodology", "signature"]):
                    continue

                if self.is_demographic_line(raw_test) or self.is_invalid_test_name(raw_test, metadata.patient_name):
                    continue

                raw_val = str(row[col_val]).strip() if col_val != -1 and col_val < len(row) and row[col_val] is not None else ""
                raw_unit = str(row[col_unit]).strip() if col_unit != -1 and col_unit < len(row) and row[col_unit] is not None else ""
                raw_range = str(row[col_range]).strip() if col_range != -1 and col_range < len(row) and row[col_range] is not None else ""
                raw_flag = str(row[col_flag]).strip() if col_flag != -1 and col_flag < len(row) and row[col_flag] is not None else None

                parsed_val = None
                needs_verification = False
                reasons = []

                num_match = re.search(r"[-+]?\d*\.?\d+", raw_val.replace(",", ""))
                if num_match:
                    try:
                        parsed_val = float(num_match.group())
                    except ValueError:
                        needs_verification = True
                        reasons.append("Could not parse numeric result value.")
                else:
                    needs_verification = True
                    reasons.append("Non-numeric or missing observed value.")

                ref_min, ref_max = self.parse_reference_range(raw_range)
                canonical_key, canon_data = self.find_canonical_match(raw_test)

                # Skip non-test rows (e.g. table headers or metadata rows in table)
                if not canon_data and not raw_unit and ref_min is None and ref_max is None:
                    continue

                category = "General Laboratory"
                desc = None
                questions = []
                if canon_data:
                    category = canon_data.get("category", "General Laboratory")
                    desc = canon_data.get("description")
                    questions = canon_data.get("questions_for_doctor", [])
                    if not raw_unit and canon_data.get("unit"):
                        raw_unit = canon_data.get("unit")
                    if (ref_min is None or ref_max is None) and canon_data.get("default_range"):
                        ref_min, ref_max = canon_data["default_range"][0], canon_data["default_range"][1]
                        raw_range = f"{ref_min} - {ref_max}"
                        needs_verification = True
                        reasons.append("Reference range supplied from clinical standard; please verify with original report.")

                if ref_min is None or ref_max is None:
                    needs_verification = True
                    reasons.append("Reference range missing or ambiguous in report.")

                items.append(BloodTestItem(
                    id=str(uuid.uuid4())[:8],
                    test_name=raw_test,
                    raw_name=raw_test,
                    category=category,
                    value=parsed_val,
                    raw_value=raw_val,
                    unit=raw_unit if raw_unit and raw_unit.lower() != "none" else None,
                    ref_min=ref_min,
                    ref_max=ref_max,
                    ref_range_text=raw_range if raw_range and raw_range.lower() != "none" else None,
                    lab_flag=raw_flag if raw_flag and raw_flag.lower() != "none" else None,
                    confidence=ExtractionConfidence.MEDIUM if needs_verification else ExtractionConfidence.HIGH,
                    needs_verification=needs_verification,
                    verification_reason="; ".join(reasons) if reasons else None,
                    description=desc,
                    questions_for_doctor=questions,
                ))

        return metadata, items

    def extract_from_csv(self, file_bytes: bytes, filename: str) -> Tuple[ReportMetadata, List[BloodTestItem]]:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception:
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), sep=None, engine="python")
            except Exception as e:
                raise ValueError(f"Could not parse CSV file: {str(e)}")

        col_map = {}
        for col in df.columns:
            clean_col = str(col).strip().lower().replace("_", " ")
            if any(term in clean_col for term in ["test", "parameter", "analyte", "investigation"]):
                col_map["test"] = col
            elif any(term in clean_col for term in ["result", "value", "reading", "observed"]):
                col_map["value"] = col
            elif any(term in clean_col for term in ["unit"]):
                col_map["unit"] = col
            elif any(term in clean_col for term in ["reference", "range", "interval", "normal"]):
                col_map["range"] = col
            elif any(term in clean_col for term in ["flag", "status"]):
                col_map["flag"] = col

        if "test" not in col_map or "value" not in col_map:
            if len(df.columns) >= 2:
                col_map["test"] = df.columns[0]
                col_map["value"] = df.columns[1]
                if len(df.columns) >= 3:
                    col_map["unit"] = df.columns[2]
                if len(df.columns) >= 4:
                    col_map["range"] = df.columns[3]
            else:
                raise ValueError("CSV must contain at least 'Test' and 'Value' columns.")

        items: List[BloodTestItem] = []
        for _, row in df.iterrows():
            raw_test = str(row[col_map["test"]]).strip()
            if not raw_test or raw_test.lower() in ["nan", "none", ""]:
                continue

            raw_val = str(row[col_map["value"]]).strip() if "value" in col_map else ""
            raw_unit = str(row[col_map["unit"]]).strip() if "unit" in col_map and pd.notna(row[col_map["unit"]]) else ""
            raw_range = str(row[col_map["range"]]).strip() if "range" in col_map and pd.notna(row[col_map["range"]]) else ""
            raw_flag = str(row[col_map["flag"]]).strip() if "flag" in col_map and pd.notna(row[col_map["flag"]]) else None

            parsed_val = None
            needs_verification = False
            reasons = []

            num_match = re.search(r"[-+]?\d*\.?\d+", raw_val.replace(",", ""))
            if num_match:
                try:
                    parsed_val = float(num_match.group())
                except ValueError:
                    needs_verification = True
                    reasons.append("Could not parse numeric result value.")
            else:
                needs_verification = True
                reasons.append("Non-numeric or empty result.")

            ref_min, ref_max = self.parse_reference_range(raw_range)
            canonical_key, canon_data = self.find_canonical_match(raw_test)
            display_name = raw_test
            category = "General Laboratory"
            desc = None
            questions = []

            if canon_data:
                category = canon_data.get("category", "General Laboratory")
                desc = canon_data.get("description")
                questions = canon_data.get("questions_for_doctor", [])
                if not raw_unit and canon_data.get("unit"):
                    raw_unit = canon_data.get("unit")
                if (ref_min is None or ref_max is None) and canon_data.get("default_range"):
                    ref_min, ref_max = canon_data["default_range"][0], canon_data["default_range"][1]
                    raw_range = f"{ref_min} - {ref_max}"
                    needs_verification = True
                    reasons.append("Reference range supplied from clinical standard; please verify with original report.")

            if ref_min is None or ref_max is None:
                needs_verification = True
                reasons.append("Reference range missing in report. Please confirm range.")

            item = BloodTestItem(
                id=str(uuid.uuid4())[:8],
                test_name=display_name,
                raw_name=raw_test,
                category=category,
                value=parsed_val,
                raw_value=raw_val,
                unit=raw_unit if raw_unit and raw_unit.lower() != "nan" else None,
                ref_min=ref_min,
                ref_max=ref_max,
                ref_range_text=raw_range if raw_range and raw_range.lower() != "nan" else None,
                lab_flag=raw_flag if raw_flag and raw_flag.lower() != "nan" else None,
                confidence=ExtractionConfidence.MEDIUM if needs_verification else ExtractionConfidence.HIGH,
                needs_verification=needs_verification,
                verification_reason="; ".join(reasons) if reasons else None,
                description=desc,
                questions_for_doctor=questions,
            )
            items.append(item)

        metadata = ReportMetadata(
            filename=filename,
            file_type="CSV",
            patient_name=None,
            collection_date=None,
            lab_name=None,
        )
        return metadata, items

    def extract_from_text(self, text: str, filename: str, file_type: str = "PDF") -> Tuple[ReportMetadata, List[BloodTestItem]]:
        """
        Multi-modal text/OCR extraction:
        Combines precision regex lab line extraction with the trained ML token classifier
        and column-stacked sequential pattern recognition.
        """
        metadata = self._extract_metadata_from_text(text, filename, file_type)
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        items: List[BloodTestItem] = []
        seen_keys = set()
        seen_raw_names = set()

        # 1. High-Precision Structured Line Parsing
        for line in lines:
            if self.is_demographic_line(line):
                continue

            parsed = self.parse_lab_line(line)
            if not parsed:
                continue

            raw_name = parsed["test_name"]
            if self.is_invalid_test_name(raw_name, metadata.patient_name):
                continue

            canon_key, canon_data = self.find_canonical_match(raw_name)

            key_identifier = canon_key if canon_key else raw_name.lower()
            if key_identifier in seen_keys:
                continue

            ref_min = parsed["ref_min"]
            ref_max = parsed["ref_max"]
            ref_text = parsed["ref_range_text"]
            unit = parsed["unit"]
            needs_verification = False
            reasons = []

            category = "General Laboratory"
            desc = None
            questions = []

            if canon_data:
                category = canon_data.get("category", category)
                desc = canon_data.get("description")
                questions = canon_data.get("questions_for_doctor", [])
                if not unit and canon_data.get("unit"):
                    unit = canon_data.get("unit")
                if (ref_min is None or ref_max is None) and canon_data.get("default_range"):
                    ref_min, ref_max = canon_data["default_range"][0], canon_data["default_range"][1]
                    ref_text = f"{ref_min} - {ref_max}"
                    needs_verification = True
                    reasons.append("Reference range supplied from clinical standard; please verify with report.")

            if ref_min is None or ref_max is None:
                needs_verification = True
                reasons.append("Reference range was not detected on this line.")

            item = BloodTestItem(
                id=str(uuid.uuid4())[:8],
                test_name=raw_name,
                raw_name=raw_name,
                category=category,
                value=parsed["value"],
                raw_value=parsed["raw_value"],
                unit=unit,
                ref_min=ref_min,
                ref_max=ref_max,
                ref_range_text=ref_text,
                lab_flag=parsed["lab_flag"],
                confidence=ExtractionConfidence.MEDIUM if needs_verification else ExtractionConfidence.HIGH,
                needs_verification=needs_verification,
                verification_reason="; ".join(reasons) if reasons else None,
                description=desc,
                questions_for_doctor=questions,
            )
            items.append(item)
            seen_keys.add(key_identifier)
            seen_raw_names.add(raw_name.lower())

        # 2. Complementary ML Token Classification
        if self.ml_engine and self.ml_engine.is_loaded:
            try:
                ml_meta, ml_items = self.ml_engine.extract_from_lines(lines)
                if not metadata.patient_name and ml_meta.patient_name:
                    metadata.patient_name = ml_meta.patient_name
                if not metadata.collection_date and ml_meta.collection_date:
                    metadata.collection_date = ml_meta.collection_date
                if not metadata.lab_name and ml_meta.lab_name:
                    metadata.lab_name = ml_meta.lab_name

                for ml_item in ml_items:
                    if self.is_demographic_line(ml_item.test_name) or self.is_invalid_test_name(ml_item.test_name, metadata.patient_name):
                        continue
                    canon_key, canon_data = self.find_canonical_match(ml_item.test_name)
                    key_id = canon_key if canon_key else ml_item.test_name.lower()
                    if key_id not in seen_keys and ml_item.test_name.lower() not in seen_raw_names:
                        if canon_data:
                            ml_item.category = canon_data.get("category", ml_item.category)
                            ml_item.description = canon_data.get("description")
                            ml_item.questions_for_doctor = canon_data.get("questions_for_doctor", [])
                            if not ml_item.unit and canon_data.get("unit"):
                                ml_item.unit = canon_data.get("unit")
                            if (ml_item.ref_min is None or ml_item.ref_max is None) and canon_data.get("default_range"):
                                ml_item.ref_min, ml_item.ref_max = canon_data["default_range"][0], canon_data["default_range"][1]
                                ml_item.ref_range_text = f"{ml_item.ref_min} - {ml_item.ref_max}"
                        items.append(ml_item)
                        seen_keys.add(key_id)
                        seen_raw_names.add(ml_item.test_name.lower())
            except Exception as e:
                logger.warning(f"ML extraction fallback encountered warning: {e}")

        # 3. Column-stacked Sequential Pattern Fallback
        i = 0
        while i < len(lines):
            line = lines[i]
            if self.is_demographic_line(line) or self.is_invalid_test_name(line, metadata.patient_name):
                i += 1
                continue
            if not re.search(r"\d", line):
                canonical_key, canon_data = self.find_canonical_match(line)
                key_id = canonical_key if canonical_key else line.lower()
                if canon_data and key_id not in seen_keys:
                    val = None
                    raw_val = None
                    unit = canon_data.get("unit")
                    ref_min = None
                    ref_max = None
                    range_text = None
                    flag = None
                    offset = 1

                    while i + offset < len(lines) and offset <= 4:
                        nxt = lines[i + offset]
                        if val is None and re.match(r"^[-+]?\d*\.?\d+$", nxt):
                            try:
                                val = float(nxt)
                                raw_val = nxt
                                offset += 1
                                continue
                            except ValueError:
                                pass
                        if nxt in ["g/dL", "%", "million/mcL", "x10^3/mcL", "fL", "pg", "mg/dL", "U/L", "mEq/L", "uIU/mL"]:
                            unit = nxt
                            offset += 1
                            continue
                        rm = re.search(r"([0-9]+\.?[0-9]*)\s*[-–—to]+\s*([0-9]+\.?[0-9]*)", nxt)
                        if rm and ref_min is None:
                            ref_min, ref_max = float(rm.group(1)), float(rm.group(2))
                            range_text = nxt
                            offset += 1
                            continue
                        if nxt.upper() in ["LOW", "L", "HIGH", "H", "NORMAL", "NORM"]:
                            flag = nxt.upper()
                            offset += 1
                            continue
                        break

                    if val is not None:
                        needs_verification = (ref_min is None or ref_max is None)
                        if (ref_min is None or ref_max is None) and canon_data.get("default_range"):
                            ref_min, ref_max = canon_data["default_range"][0], canon_data["default_range"][1]
                            range_text = f"{ref_min} - {ref_max}"

                        items.append(BloodTestItem(
                            id=str(uuid.uuid4())[:8],
                            test_name=line,
                            raw_name=line,
                            category=canon_data.get("category", "General Laboratory"),
                            value=val,
                            raw_value=raw_val,
                            unit=unit,
                            ref_min=ref_min,
                            ref_max=ref_max,
                            ref_range_text=range_text,
                            lab_flag=flag,
                            confidence=ExtractionConfidence.MEDIUM if needs_verification else ExtractionConfidence.HIGH,
                            needs_verification=needs_verification,
                            verification_reason="Reference range not fully detected." if needs_verification else None,
                            description=canon_data.get("description"),
                            questions_for_doctor=canon_data.get("questions_for_doctor", []),
                        ))
                        seen_keys.add(key_id)
                        seen_raw_names.add(line.lower())
                        i += offset
                        continue
            i += 1

        return metadata, items

    def extract_from_ocr_lines(self, ocr_results: List[Dict[str, Any]], filename: str, file_type: str = "Image") -> Tuple[ReportMetadata, List[BloodTestItem]]:
        """
        Directly process deep-learning OCR detected lines and boxes using the multi-tier extraction pipeline.
        """
        lines = [item["text"] for item in ocr_results if item.get("text")]
        combined_text = "\n".join(lines)
        return self.extract_from_text(combined_text, filename, file_type=file_type)
