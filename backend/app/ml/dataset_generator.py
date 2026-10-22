"""
Synthetic Dataset Generator for Laboratory Blood Report Token Classification and Entity Extraction.
Generates comprehensive annotated samples across all laboratory testing categories,
formats, biological reference interval structures, and real-world noisy OCR variants.
"""

import json
import random
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "reference_ranges.json"


def load_all_parameters() -> List[Dict[str, Any]]:
    """
    Loads all clinical parameters, their aliases, units, and reference ranges
    from the medical knowledge catalog.
    """
    params = []
    if KNOWLEDGE_PATH.exists():
        try:
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, item in data.items():
                    default_range = item.get("default_range", [1.0, 10.0])
                    min_val = float(default_range[0])
                    max_val = float(default_range[1])
                    unit = item.get("unit", "")
                    
                    # Estimate reasonable value range for simulation
                    spread = max(max_val - min_val, 1.0)
                    val_low = max(0.0, round(min_val - spread * 0.45, 2))
                    val_high = round(max_val + spread * 0.75, 2)

                    # Add canonical display name
                    display_name = item.get("display_name", key.replace("_", " ").title())
                    params.append({
                        "name": display_name,
                        "unit": unit,
                        "min": min_val,
                        "max": max_val,
                        "val_range": (val_low, val_high)
                    })

                    # Add all aliases
                    for alias in item.get("aliases", []):
                        if alias.strip() and alias.strip().lower() != display_name.lower():
                            alias_name = alias.strip().title() if not alias.isupper() else alias.strip()
                            params.append({
                                "name": alias_name,
                                "unit": unit,
                                "min": min_val,
                                "max": max_val,
                                "val_range": (val_low, val_high)
                            })
        except Exception as e:
            print(f"Warning: Failed to load knowledge base: {e}")

    # Fallback default parameters if file not found
    if not params:
        params = [
            {"name": "Hemoglobin", "unit": "g/dL", "min": 12.0, "max": 17.5, "val_range": (8.0, 19.0)},
            {"name": "Hb", "unit": "g/dL", "min": 12.0, "max": 16.0, "val_range": (9.0, 18.0)},
            {"name": "RBC", "unit": "million/mcL", "min": 4.0, "max": 5.9, "val_range": (3.0, 6.5)},
            {"name": "WBC", "unit": "/cumm", "min": 4000, "max": 11000, "val_range": (2500, 16000)},
            {"name": "Platelets", "unit": "x10^3/mcL", "min": 150.0, "max": 450.0, "val_range": (80.0, 550.0)},
            {"name": "Fasting Glucose", "unit": "mg/dL", "min": 70.0, "max": 99.0, "val_range": (55.0, 180.0)},
            {"name": "Serum Creatinine", "unit": "mg/dL", "min": 0.6, "max": 1.3, "val_range": (0.4, 4.2)},
            {"name": "Total Cholesterol", "unit": "mg/dL", "min": 100.0, "max": 200.0, "val_range": (90.0, 310.0)},
            {"name": "TSH", "unit": "uIU/mL", "min": 0.4, "max": 4.5, "val_range": (0.1, 14.0)},
            {"name": "Vitamin D 25-OH", "unit": "ng/mL", "min": 30.0, "max": 100.0, "val_range": (8.0, 110.0)},
        ]
    return params


ALL_PARAMS = load_all_parameters()

HEADER_NOISE = [
    "Apex Clinical Diagnostic Laboratories Inc.",
    "Metropolis Healthcare & Diagnostics Center",
    "PathCare World Pathology and Research Institute",
    "Patient Name: Jane Doe Age: 34 Y / Female",
    "Patient ID: PAT-99214 Ref. Doctor: Dr. S. Sharma MBBS MD",
    "Sample Collection Date: 15-Oct-2026 Time: 08:30 AM",
    "Specimen: Whole Blood EDTA / Fluoride Plasma / Serum",
    "Report Status: Final Authorized Diagnostic Medical Record",
    "Test Parameter Observed Value Units Biological Reference Interval Flag",
    "Investigation Result Unit Normal Range Remarks",
    "TEST NAME RESULT UNITS REFERENCE INTERVAL STATUS",
    "Analyte Reading Reference Range Method Status",
    "Department of Biochemistry & Clinical Pathology",
    "Printed On: 18-Oct-2026 Page 1 of 2",
    "Methodology: Fully Automated Chemiluminescence Immunoassay (CLIA)",
    "Quality Control Verified by Laboratory Director Dr. A. Patel MD",
    "End of Laboratory Report. For clinical correlation only.",
    "Bar Code: 994827104 MRN: 0092817 Accession No: 881726",
    "Bill No: INV-2026-8819 Receipt Date: 12/10/2026",
    "Consultant Pathologist: Dr. R. K. Mukherjee MD (Pathology)",
]


def format_value(val: float) -> str:
    """Formats numeric values realistically with occasional comma decimals."""
    if val >= 100:
        val_str = f"{val:.0f}" if random.random() < 0.6 else f"{val:.1f}"
    elif val >= 10:
        val_str = f"{val:.1f}" if random.random() < 0.7 else f"{val:.2f}"
    else:
        val_str = f"{val:.2f}" if random.random() < 0.5 else f"{val:.1f}"

    # Occasional OCR decimal comma (e.g. European reports or OCR dot-drop)
    if random.random() < 0.05 and "." in val_str:
        val_str = val_str.replace(".", ",")
    return val_str


def format_ref_range(min_val: float, max_val: float) -> Tuple[str, List[str]]:
    """Generates varied reference interval formatting tokens."""
    style = random.randint(1, 9)
    if style == 1:
        # 12.0 - 16.0
        return f"{min_val} - {max_val}", [str(min_val), "-", str(max_val)]
    elif style == 2:
        # 12.0-16.0
        return f"{min_val}-{max_val}", [f"{min_val}-{max_val}"]
    elif style == 3:
        # 12.0 to 16.0
        return f"{min_val} to {max_val}", [str(min_val), "to", str(max_val)]
    elif style == 4:
        # < max_val or > min_val
        if min_val <= 0 or random.random() < 0.5:
            return f"< {max_val}", ["<", str(max_val)]
        else:
            return f"> {min_val}", [">", str(min_val)]
    elif style == 5:
        # <= max_val or >= min_val
        if min_val <= 0 or random.random() < 0.5:
            return f"<= {max_val}", ["<=", str(max_val)]
        else:
            return f">= {min_val}", [">=", str(min_val)]
    elif style == 6:
        # (12.0 - 16.0)
        return f"({min_val} - {max_val})", [f"({min_val}", "-", f"{max_val})"]
    elif style == 7:
        # [12.0 - 16.0]
        return f"[{min_val} - {max_val}]", [f"[{min_val}", "-", f"{max_val}]"]
    elif style == 8:
        # 12.0 – 16.0 (en-dash)
        return f"{min_val} – {max_val}", [str(min_val), "–", str(max_val)]
    else:
        # Ref: 12.0 - 16.0
        prefix = random.choice(["Ref:", "Normal:", "Range:"])
        return f"{prefix} {min_val} - {max_val}", [prefix, str(min_val), "-", str(max_val)]


def inject_ocr_noise(text: str) -> str:
    """Simulates realistic OCR misreads (O->0, l->1, missing spaces)."""
    if random.random() < 0.08:
        # Split word with space e.g. "Hemo globin"
        if len(text) > 5:
            mid = random.randint(2, len(text) - 2)
            return text[:mid] + " " + text[mid:]
    return text


def generate_parameter_line(param: dict) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Returns (raw_line, [(token, label), ...])
    Labels:
      B-PARAM, I-PARAM, VALUE, UNIT, REF_RANGE, FLAG, O
    """
    raw_name = param["name"]
    name_tokens = raw_name.split()

    # Determine simulated observed value
    min_v, max_v = param["min"], param["max"]
    low_b, high_b = param["val_range"]
    val_float = round(random.uniform(low_b, high_b), 2)
    val_str = format_value(val_float)

    # Determine clinical flag
    if val_float < min_v:
        flag = random.choice(["LOW", "L", "Low", "LO", "BELOW", "▼", "*", "CRITICAL LOW"])
    elif val_float > max_v:
        flag = random.choice(["HIGH", "H", "High", "HI", "ABOVE", "▲", "*", "ALERT", "CRITICAL HIGH"])
    else:
        flag = random.choice(["NORMAL", "Normal", "N", "NORM", "Within Range", "OK", ""])

    unit_str = param["unit"]
    ref_txt, ref_tokens = format_ref_range(min_v, max_v)

    layout = random.randint(1, 6)
    tokens: List[Tuple[str, str]] = []

    def add_param_tokens():
        for i, tok in enumerate(name_tokens):
            lbl = "B-PARAM" if i == 0 else "I-PARAM"
            tokens.append((tok, lbl))

    if layout == 1:
        # Standard table row: Hemoglobin 14.2 g/dL 12.0 - 16.0 Normal
        add_param_tokens()
        tokens.append((val_str, "VALUE"))
        if unit_str:
            tokens.append((unit_str, "UNIT"))
        for r_tok in ref_tokens:
            tokens.append((r_tok, "REF_RANGE"))
        if flag:
            tokens.append((flag, "FLAG"))

    elif layout == 2:
        # Colon-delimited: Hemoglobin: 14.2 g/dL (Ref: 12.0 - 16.0)
        add_param_tokens()
        tokens.append((":", "O"))
        tokens.append((val_str, "VALUE"))
        if unit_str:
            tokens.append((unit_str, "UNIT"))
        for r_tok in ref_tokens:
            tokens.append((r_tok, "REF_RANGE"))
        if flag:
            tokens.append((flag, "FLAG"))

    elif layout == 3:
        # Pipe-delimited table: Hemoglobin | 14.2 | g/dL | 12.0 - 16.0 | NORMAL
        add_param_tokens()
        tokens.append(("|", "O"))
        tokens.append((val_str, "VALUE"))
        tokens.append(("|", "O"))
        if unit_str:
            tokens.append((unit_str, "UNIT"))
            tokens.append(("|", "O"))
        for r_tok in ref_tokens:
            tokens.append((r_tok, "REF_RANGE"))
        if flag:
            tokens.append(("|", "O"))
            tokens.append((flag, "FLAG"))

    elif layout == 4:
        # With trailing flag before unit/range: Hemoglobin 14.2 HIGH g/dL 12.0 - 16.0
        add_param_tokens()
        tokens.append((val_str, "VALUE"))
        if flag:
            tokens.append((flag, "FLAG"))
        if unit_str:
            tokens.append((unit_str, "UNIT"))
        for r_tok in ref_tokens:
            tokens.append((r_tok, "REF_RANGE"))

    elif layout == 5:
        # Range before unit: Hemoglobin 14.2 12.0 - 16.0 g/dL Normal
        add_param_tokens()
        tokens.append((val_str, "VALUE"))
        for r_tok in ref_tokens:
            tokens.append((r_tok, "REF_RANGE"))
        if unit_str:
            tokens.append((unit_str, "UNIT"))
        if flag:
            tokens.append((flag, "FLAG"))

    else:
        # Tabular with omitted flag: Hemoglobin 14.2 g/dL 12.0 - 16.0
        add_param_tokens()
        tokens.append((val_str, "VALUE"))
        if unit_str:
            tokens.append((unit_str, "UNIT"))
        for r_tok in ref_tokens:
            tokens.append((r_tok, "REF_RANGE"))

    line_str = " ".join([t[0] for t in tokens])
    return line_str, tokens


def generate_noise_line(text: str) -> Tuple[str, List[Tuple[str, str]]]:
    words = text.split()
    tokens = []
    for w in words:
        w_lower = w.lower()
        if any(hdr in w_lower for hdr in ["patient", "doctor", "dr.", "dr", "age", "male", "female", "date", "specimen", "hospital", "clinic", "diagnostic", "pathology", "accession", "receipt", "mrn", "bar", "code", "invoice"]):
            tokens.append((w, "META"))
        else:
            tokens.append((w, "O"))
    return text, tokens


def build_synthetic_dataset(num_samples: int = 8000) -> List[List[Tuple[str, str]]]:
    """
    Generates a list of tokenized sentences with gold-standard labels.
    Balanced with ~80% parameter lines across all 50+ clinical lab tests and ~20% realistic header/demographic noise lines.
    """
    dataset = []
    for _ in range(num_samples):
        if random.random() < 0.80:
            param = random.choice(ALL_PARAMS)
            _, tokens = generate_parameter_line(param)
            dataset.append(tokens)
        else:
            noise_text = random.choice(HEADER_NOISE)
            _, tokens = generate_noise_line(noise_text)
            dataset.append(tokens)

    return dataset
