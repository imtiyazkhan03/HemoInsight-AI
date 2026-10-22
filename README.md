# HemoInsight AI — Smart Blood Report Analyzer
**Next-Generation Clinical Biomarker Intelligence & Laboratory Interpretation System**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/imtiyazkhan03/HemoInsight-AI)

> **Objective:** An intelligent, evidence-supported web application that processes laboratory blood test reports (PDF, CSV, PNG, JPG, JPEG), extracts test parameters and biological reference intervals using deep learning OCR and multimodal vision AI, classifies results into **Within Range**, **Low**, **High**, or **Needs Review**, flags uncertain entries for human verification, correlates findings with physical symptoms, explains findings in clear plain language, and generates downloadable medical summaries.

---

## 🔬 Core Workflow Overview

1. **Upload Report:** Users upload blood reports in PDF (native digital vector or scanned raster), CSV, PNG, JPG, or JPEG formats.
2. **Multi-Engine Parameter Extraction:**
   - **PyMuPDF (`fitz`)**: Extracts vector text and structured tabular grid rows.
   - **Deep Learning OCR (RapidOCR / Tesseract fallback)**: Preprocesses rasterized pages and scans using PIL (contrast enhancement, sharpening, binarization).
   - **Trained Machine Learning Model (Random Forest)**: Token-level classification and bio-entity tagging with 95%+ accuracy.
   - **Gemini Multimodal Vision AI**: State-of-the-art fallback for complex, handwritten, or degraded lab documents.
   - **Pandas Parser**: Processes structured CSV files directly.
3. **Quality & Uncertainty Verification:**
   - Any ambiguous readings or missing laboratory reference ranges are flagged with confidence scoring.
   - Users can inspect, edit, delete, or supply missing intervals via the **Verification & Edit Modal** before final analysis.
4. **Deterministic Classification:**
   - Strictly compares patient readings against the **laboratory's supplied biological reference ranges** (never assuming a single universal threshold).
   - Classifies each parameter into `WITHIN_RANGE`, `LOW`, `HIGH`, or `NEEDS_REVIEW`.
5. **Report-Level Outcome Determination:**
   - **Outcome A:** *No Out-of-Range Results Detected* (Calm teal/emerald styling).
   - **Outcome B:** *Some Results Need Attention* (Amber/rose accent with list of affected biomarkers).
   - **Outcome C:** *Unable to Fully Analyze This Report* (Incomplete data warning; prompts user review).
6. **Clinical Correlation & Symptoms Checklist:**
   - Automatically correlates flagged biomarkers with common physical symptoms.
   - Interactive checklist allowing patients to check off symptoms and copy a structured brief for physician consultation.
7. **Plain-Language Medical Context:**
   - Structured, evidence-supported explanations from our medical knowledge catalog (covering 40+ key hematology, biochemistry, metabolic, and liver/kidney biomarkers).
   - Non-diagnostic, strictly safe wording explaining what low/high means without diagnosing or prescribing.
   - Personalized checklist of **Questions to Discuss with Your Doctor**.
8. **Export Capabilities:**
   - **Download PDF Summary:** Generates a clean, hospital-grade formatted medical report using ReportLab.
   - **Export CSV:** Exports complete numerical and status data for records.

---

## 🛠️ Architecture & Technology Stack

```
HemoInsight AI/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI API endpoints, CORS, & routing
│   │   ├── models/schemas.py                # Pydantic schemas for items, results, and outcomes
│   │   ├── ml/
│   │   │   ├── dataset_generator.py         # Synthetic lab token training dataset generator
│   │   │   ├── train_model.py               # Random Forest token classifier training pipeline
│   │   │   └── model_inference.py           # Real-time ML inference & entity extractor
│   │   ├── services/
│   │   │   ├── ocr_service.py               # RapidOCR & Tesseract OCR image preprocessing
│   │   │   ├── pdf_service.py               # PyMuPDF table extraction & page rasterization
│   │   │   ├── gemini_vision_service.py     # Gemini Multimodal Vision AI extraction
│   │   │   ├── extraction_service.py        # Tabular parser & regex token matching
│   │   │   ├── classification_service.py    # Deterministic reference interval classifier
│   │   │   ├── medical_explanation_service.py # Evidence-based medical plain-language engine
│   │   │   └── report_service.py            # ReportLab PDF & CSV generator
│   │   ├── knowledge/
│   │   │   └── reference_ranges.json        # Structured medical knowledge catalog (40+ biomarkers)
│   │   └── samples/                         # Pre-generated synthetic test files
│   ├── test_pipeline.py                     # Pipeline integration tests
│   ├── test_api.py                          # FastAPI endpoint tests
│   ├── test_ml_and_symptoms.py              # ML accuracy & symptom correlation tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx                   # Top navigation with live backend status & brand badge
│   │   │   ├── LandingPage.tsx              # Hero, transformation demo, 3-step guide, sample suite
│   │   │   ├── UploadSection.tsx            # Drag & drop upload, validation, sample buttons
│   │   │   ├── ResultsDashboard.tsx         # Dashboard with metrics, table & actions
│   │   │   ├── OverallResultBanner.tsx      # Outcome A, B, or C banner
│   │   │   ├── ParameterTable.tsx           # Searchable & filterable findings table
│   │   │   ├── ParameterDetailModal.tsx     # Parameter detail popup with range visualizer
│   │   │   ├── RangeVisualizer.tsx          # Visual gauge mapping patient value to interval
│   │   │   ├── SymptomsChecklist.tsx        # Interactive correlated physical symptoms checklist
│   │   │   ├── ExplanationsSection.tsx      # Expandable "What Do Your Results Mean?" cards
│   │   │   ├── VerificationModal.tsx        # Editable modal to review uncertain OCR data
│   │   │   ├── MedicalDisclaimer.tsx        # Educational safety disclaimer
│   │   │   └── Footer.tsx                   # Footer with project metadata & privacy statement
│   │   ├── services/api.ts                  # Frontend API client (upload, finalize, export)
│   │   ├── types/index.ts                   # TypeScript interfaces
│   │   ├── App.tsx                          # App state & view router
│   │   └── index.css                        # Tailwind CSS styles & typography
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── README.md
```

---

## 🚀 Running the Project Locally

### 1. Backend Server (Python FastAPI)

```bash
# From workspace root
cd "c:\Users\Imtiyaz\Imtiyaz_projects\HemoInsight AI"

# Activate Python environment and start backend
$env:PYTHONPATH="."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend runs on `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

### 2. Frontend Application (React + Vite + TypeScript)

```bash
cd "c:\Users\Imtiyaz\Imtiyaz_projects\HemoInsight AI\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
```
The web application will open on `http://127.0.0.1:5173`.

### 3. Automated Test Suite

```bash
# Run all backend unit and integration tests
python -m pytest backend/
```

---

## 🧪 Testing Scenarios Included

Four preconfigured synthetic test scenarios are built directly into the UI for instant 1-click evaluation:

1. **Complete Blood Count (CBC) with Mild Anemia & Low Platelets**
   - *Outcome:* `Some Results Need Attention` (Outcome B)
   - Low hemoglobin, low RBC, low hematocrit, low MCV, low platelets, normal WBC.
2. **Comprehensive Routine Health Panel (All Normal)**
   - *Outcome:* `No Out-of-Range Results Detected` (Outcome A)
   - Normal glucose, hemoglobin, creatinine, cholesterol, ALT, and potassium.
3. **Lipid & Metabolic Panel (High Cholesterol & Glucose)**
   - *Outcome:* `Some Results Need Attention` (Outcome B)
   - High LDL, high triglycerides, high fasting glucose, low HDL.
4. **Smudged / Incomplete Report (Missing Ranges)**
   - *Outcome:* `Unable to Fully Analyze This Report` (Outcome C)
   - Triggers the **Verification & Edit Modal** so the reviewer can supply missing bounds.

---

## ⚖️ Medical Safety Standards
- **Non-Diagnostic:** The application highlights that an abnormal result alone cannot confirm any disease without clinical correlation.
- **No Automatic Prescriptions:** Never provides drug prescriptions or promises of cure.
- **Reference Range Integrity:** Never forces universal reference ranges; adheres strictly to the laboratory's printed boundaries.
