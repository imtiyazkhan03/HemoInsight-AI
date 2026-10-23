import os
import io
import json
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Response, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .models.schemas import (
    AnalysisResponse,
    ReportMetadata,
    ReportSummary,
    BloodTestItem,
    VerifyAndFinalizeRequest,
    TestStatus,
    OverallOutcome,
    ExtractionConfidence,
    SampleReport,
    AssociatedCondition,
    CorrelateConditionsRequest,
)
from .services.ocr_service import OCRService
from .services.pdf_service import PDFService
from .services.extraction_service import ExtractionService
from .services.classification_service import ClassificationService
from .services.medical_explanation_service import MedicalExplanationService
from .services.report_service import ReportService
from .services.gemini_vision_service import GeminiVisionService
from .ml.model_inference import MLInferenceEngine
from .ml.train_model import train_and_save_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HemoInsightAI")

app = FastAPI(
    title="HemoInsight AI — Smart Blood Report Analyzer API",
    description="Backend API for automated laboratory blood report extraction, verification, deterministic classification, and plain-language medical explanation powered by VitalScan Engine.",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modular services
ocr_service = OCRService()
pdf_service = PDFService(ocr_service=ocr_service)
extraction_service = ExtractionService()
classification_service = ClassificationService()
medical_explanation_service = MedicalExplanationService()
report_service = ReportService()
gemini_vision_service = GeminiVisionService()
ml_engine = MLInferenceEngine.get_instance()

MEDICAL_DISCLAIMER = (
    "HemoInsight AI is an educational laboratory report interpretation tool for academic Experiment 9. "
    "It is NOT a medical diagnostic system, does not establish a diagnosis, and does not prescribe treatment. "
    "Laboratory reference intervals vary across health systems and testing instruments. "
    "Always consult a qualified healthcare professional regarding any clinical questions, symptoms, or lab findings."
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HemoInsight AI Blood Report Analyzer",
        "engine": "VitalScan Precision OCR & ML Classifier",
        "ocr_available": ocr_service.is_available,
        "ocr_engine": ocr_service.engine_name,
        "ml_model_loaded": ml_engine.is_loaded,
        "ml_model_accuracy": ml_engine.accuracy,
        "gemini_vision_ready": gemini_vision_service.is_configured(),
        "version": "1.0.0"
    }


@app.get("/api/model/status")
def get_model_status():
    """
    Returns the real-time operational status of all AI/ML models:
    - Trained Local ML Token Classifier (Random Forest)
    - Deep Learning OCR Engine (RapidOCR ONNX)
    - Gemini Multimodal Vision AI Model
    """
    return {
        "local_ml_model": {
            "loaded": ml_engine.is_loaded,
            "architecture": "Random Forest Entity Extractor & Token Classifier",
            "token_accuracy": round(ml_engine.accuracy * 100, 2),
            "classes": ml_engine.classes,
            "version": "1.0.0",
            "status": "Active & Ready" if ml_engine.is_loaded else "Unavailable",
        },
        "deep_learning_ocr": {
            "available": ocr_service.is_available,
            "engine": ocr_service.engine_name,
            "architecture": "DBNet Text Detection + CRNN Text Recognition (ONNX)",
            "supports_scanned_images": True,
        },
        "gemini_vision_ai": {
            "sdk_installed": gemini_vision_service.is_available,
            "configured": gemini_vision_service.is_configured(),
            "models_supported": ["gemini-2.5-flash", "gemini-2.0-flash"],
            "capabilities": "Zero-shot multimodal vision document intelligence",
        }
    }


@app.post("/api/model/retrain")
def retrain_model(samples: int = Query(5000, ge=1000, le=20000)):
    """
    Triggers on-demand retraining of the blood report token classification model.
    """
    try:
        accuracy, report = train_and_save_model(num_samples=samples)
        ml_engine.load_model()
        return {
            "status": "success",
            "message": "Model retrained and reloaded successfully.",
            "token_accuracy": round(accuracy * 100, 2),
            "evaluation_report": report,
        }
    except Exception as e:
        logger.error(f"Error during model retraining: {e}")
        raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")


@app.get("/api/samples", response_model=List[SampleReport])
def get_sample_reports():
    """
    Returns curated clinical blood test sample reports for demonstration and testing.
    """
    return [
        SampleReport(
            id="sample-cbc-anemia",
            title="Complete Blood Count — Anemia & Thrombocytopenia Panel",
            description="Diagnostic CBC showing microcytic anemia with reduced hemoglobin, hematocrit, and platelet count.",
            outcome_preview="Some Results Need Attention (Outcome B)",
            filename="sample_cbc_anemia.pdf",
            parameters=[
                BloodTestItem(id="s1-1", test_name="Hemoglobin", value=10.4, raw_value="10.4", unit="g/dL", ref_min=12.0, ref_max=16.0, ref_range_text="12.0 - 16.0", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s1-2", test_name="Red Blood Cell Count", value=3.75, raw_value="3.75", unit="million/mcL", ref_min=4.0, ref_max=5.4, ref_range_text="4.0 - 5.4", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s1-3", test_name="Hematocrit", value=32.5, raw_value="32.5", unit="%", ref_min=36.0, ref_max=48.0, ref_range_text="36.0 - 48.0", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s1-4", test_name="Mean Corpuscular Volume (MCV)", value=75.2, raw_value="75.2", unit="fL", ref_min=80.0, ref_max=100.0, ref_range_text="80.0 - 100.0", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s1-5", test_name="White Blood Cell Count", value=6.8, raw_value="6.8", unit="x10^3/mcL", ref_min=4.0, ref_max=11.0, ref_range_text="4.0 - 11.0", lab_flag="Normal", category="Complete Blood Count (CBC)", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s1-6", test_name="Platelets", value=128.0, raw_value="128", unit="x10^3/mcL", ref_min=150.0, ref_max=450.0, ref_range_text="150.0 - 450.0", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s1-7", test_name="Neutrophils", value=58.0, raw_value="58", unit="%", ref_min=40.0, ref_max=75.0, ref_range_text="40.0 - 75.0", lab_flag="Normal", category="Complete Blood Count (CBC)", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s1-8", test_name="Lymphocytes", value=32.0, raw_value="32", unit="%", ref_min=20.0, ref_max=45.0, ref_range_text="20.0 - 45.0", lab_flag="Normal", category="Complete Blood Count (CBC)", status=TestStatus.WITHIN_RANGE),
            ]
        ),
        SampleReport(
            id="sample-routine-checkup",
            title="Routine Annual Wellness Health Checkup",
            description="Comprehensive preventive blood screening with all CBC, liver, kidney, and glucose parameters in healthy baseline range.",
            outcome_preview="No Out-of-Range Results (Outcome A)",
            filename="sample_routine_checkup.csv",
            parameters=[
                BloodTestItem(id="s2-1", test_name="Hemoglobin", value=14.2, raw_value="14.2", unit="g/dL", ref_min=12.0, ref_max=16.5, ref_range_text="12.0 - 16.5", lab_flag="Normal", category="Complete Blood Count (CBC)", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s2-2", test_name="Fasting Glucose", value=88.0, raw_value="88", unit="mg/dL", ref_min=70.0, ref_max=99.0, ref_range_text="70 - 99", lab_flag="Normal", category="Metabolic Panel", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s2-3", test_name="Creatinine", value=0.92, raw_value="0.92", unit="mg/dL", ref_min=0.6, ref_max=1.3, ref_range_text="0.6 - 1.3", lab_flag="Normal", category="Renal Function", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s2-4", test_name="Total Cholesterol", value=178.0, raw_value="178", unit="mg/dL", ref_min=125.0, ref_max=200.0, ref_range_text="125 - 200", lab_flag="Normal", category="Lipid Profile", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s2-5", test_name="ALT", value=24.0, raw_value="24", unit="U/L", ref_min=7.0, ref_max=56.0, ref_range_text="7 - 56", lab_flag="Normal", category="Liver Function", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s2-6", test_name="Potassium", value=4.2, raw_value="4.2", unit="mEq/L", ref_min=3.5, ref_max=5.2, ref_range_text="3.5 - 5.2", lab_flag="Normal", category="Electrolytes", status=TestStatus.WITHIN_RANGE),
            ]
        ),
        SampleReport(
            id="sample-metabolic-lipid",
            title="Comprehensive Metabolic & Lipid Cardiovascular Panel",
            description="Cardiometabolic screening with elevated fasting blood glucose, cholesterol, and triglycerides.",
            outcome_preview="Some Results Need Attention (Outcome B)",
            filename="sample_metabolic_lipid.pdf",
            parameters=[
                BloodTestItem(id="s3-1", test_name="Fasting Glucose", value=156.0, raw_value="156", unit="mg/dL", ref_min=70.0, ref_max=99.0, ref_range_text="70 - 99", lab_flag="H", category="Metabolic Panel", status=TestStatus.HIGH),
                BloodTestItem(id="s3-2", test_name="HbA1c", value=7.2, raw_value="7.2", unit="%", ref_min=4.0, ref_max=5.6, ref_range_text="4.0 - 5.6", lab_flag="H", category="Metabolic Panel", status=TestStatus.HIGH),
                BloodTestItem(id="s3-3", test_name="Total Cholesterol", value=248.0, raw_value="248", unit="mg/dL", ref_min=100.0, ref_max=200.0, ref_range_text="100 - 200", lab_flag="H", category="Lipid Profile", status=TestStatus.HIGH),
                BloodTestItem(id="s3-4", test_name="Triglycerides", value=230.0, raw_value="230", unit="mg/dL", ref_min=50.0, ref_max=150.0, ref_range_text="50 - 150", lab_flag="H", category="Lipid Profile", status=TestStatus.HIGH),
                BloodTestItem(id="s3-5", test_name="HDL Cholesterol", value=36.0, raw_value="36", unit="mg/dL", ref_min=40.0, ref_max=60.0, ref_range_text="40 - 60", lab_flag="L", category="Lipid Profile", status=TestStatus.LOW),
                BloodTestItem(id="s3-6", test_name="Serum Creatinine", value=0.88, raw_value="0.88", unit="mg/dL", ref_min=0.6, ref_max=1.3, ref_range_text="0.6 - 1.3", lab_flag="Normal", category="Renal Function", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s3-7", test_name="TSH", value=2.1, raw_value="2.1", unit="uIU/mL", ref_min=0.4, ref_max=4.5, ref_range_text="0.4 - 4.5", lab_flag="Normal", category="Thyroid Profile", status=TestStatus.WITHIN_RANGE),
            ]
        ),
        SampleReport(
            id="sample-thyroid-vitamin",
            title="Thyroid & Micronutrient Deficiency Panel",
            description="Endocrine and nutritional panel highlighting suboptimal Vitamin D 25-OH and elevated TSH.",
            outcome_preview="Some Results Need Attention (Outcome B)",
            filename="sample_thyroid_vitamin.pdf",
            parameters=[
                BloodTestItem(id="s4-1", test_name="TSH", value=6.8, raw_value="6.8", unit="uIU/mL", ref_min=0.4, ref_max=4.5, ref_range_text="0.4 - 4.5", lab_flag="H", category="Thyroid Profile", status=TestStatus.HIGH),
                BloodTestItem(id="s4-2", test_name="Free T4", value=0.9, raw_value="0.9", unit="ng/dL", ref_min=0.8, ref_max=1.8, ref_range_text="0.8 - 1.8", lab_flag="Normal", category="Thyroid Profile", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s4-3", test_name="Vitamin D 25-OH", value=14.2, raw_value="14.2", unit="ng/mL", ref_min=30.0, ref_max=100.0, ref_range_text="30.0 - 100.0", lab_flag="L", category="Vitamins & Minerals", status=TestStatus.LOW),
                BloodTestItem(id="s4-4", test_name="Vitamin B12", value=420.0, raw_value="420", unit="pg/mL", ref_min=200.0, ref_max=900.0, ref_range_text="200.0 - 900.0", lab_flag="Normal", category="Vitamins & Minerals", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s4-5", test_name="Serum Ferritin", value=45.0, raw_value="45", unit="ng/mL", ref_min=15.0, ref_max=200.0, ref_range_text="15.0 - 200.0", lab_flag="Normal", category="Iron Studies", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s4-6", test_name="Calcium", value=9.2, raw_value="9.2", unit="mg/dL", ref_min=8.5, ref_max=10.5, ref_range_text="8.5 - 10.5", lab_flag="Normal", category="Electrolytes", status=TestStatus.WITHIN_RANGE),
            ]
        ),
        SampleReport(
            id="sample-typhoid-enteric",
            title="Febrile Illness & Enteric (Typhoid) Panel",
            description="Acute febrile blood panel showing leukopenia, low platelets, and reactive liver transaminitis matching enteric fever patterns.",
            outcome_preview="Some Results Need Attention (Outcome B)",
            filename="sample_typhoid_enteric.pdf",
            parameters=[
                BloodTestItem(id="s5-1", test_name="White Blood Cell Count", value=3.2, raw_value="3.2", unit="x10^3/mcL", ref_min=4.0, ref_max=11.0, ref_range_text="4.0 - 11.0", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s5-2", test_name="Platelets", value=130.0, raw_value="130", unit="x10^3/mcL", ref_min=150.0, ref_max=450.0, ref_range_text="150.0 - 450.0", lab_flag="L", category="Complete Blood Count (CBC)", status=TestStatus.LOW),
                BloodTestItem(id="s5-3", test_name="ALT (SGPT)", value=74.0, raw_value="74", unit="U/L", ref_min=7.0, ref_max=56.0, ref_range_text="7 - 56", lab_flag="H", category="Liver Function", status=TestStatus.HIGH),
                BloodTestItem(id="s5-4", test_name="AST (SGOT)", value=68.0, raw_value="68", unit="U/L", ref_min=10.0, ref_max=40.0, ref_range_text="10 - 40", lab_flag="H", category="Liver Function", status=TestStatus.HIGH),
                BloodTestItem(id="s5-5", test_name="C-Reactive Protein (CRP)", value=22.4, raw_value="22.4", unit="mg/L", ref_min=0.0, ref_max=5.0, ref_range_text="0.0 - 5.0", lab_flag="H", category="Inflammatory Markers", status=TestStatus.HIGH),
                BloodTestItem(id="s5-6", test_name="Hemoglobin", value=13.4, raw_value="13.4", unit="g/dL", ref_min=12.0, ref_max=16.0, ref_range_text="12.0 - 16.0", lab_flag="Normal", category="Complete Blood Count (CBC)", status=TestStatus.WITHIN_RANGE),
                BloodTestItem(id="s5-7", test_name="Serum Creatinine", value=0.92, raw_value="0.92", unit="mg/dL", ref_min=0.6, ref_max=1.3, ref_range_text="0.6 - 1.3", lab_flag="Normal", category="Renal Function", status=TestStatus.WITHIN_RANGE),
            ]
        ),
    ]


@app.post("/api/analyze/upload", response_model=AnalysisResponse)
async def analyze_upload(
    file: UploadFile = File(...),
    x_gemini_api_key: Optional[str] = Header(None, alias="X-Gemini-API-Key")
):
    filename = file.filename or "uploaded_report"
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    allowed_exts = ["pdf", "csv", "png", "jpg", "jpeg"]
    if ext not in allowed_exts and file.content_type:
        mime = file.content_type.lower()
        if "pdf" in mime:
            ext = "pdf"
        elif "csv" in mime or "text/plain" in mime:
            ext = "csv"
        elif "png" in mime:
            ext = "png"
        elif "jpeg" in mime or "jpg" in mime:
            ext = "jpg"

    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Supported formats are: PDF, CSV, PNG, JPG, JPEG."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    extracted_text = ""
    metadata = None
    items: List[BloodTestItem] = []

    try:
        # 1. Attempt Multimodal Gemini Vision AI if API key is provided and format is PDF/image
        if ext in ["pdf", "png", "jpg", "jpeg"] and gemini_vision_service.is_configured(x_gemini_api_key):
            logger.info("Attempting extraction with Gemini Multimodal Vision AI...")
            success, g_meta, g_items, g_msg = gemini_vision_service.extract_from_media(
                file_bytes=file_bytes,
                mime_type=ext,
                filename=filename,
                api_key=x_gemini_api_key,
            )
            if success and g_items:
                logger.info(f"Gemini Vision successfully extracted {len(g_items)} parameters.")
                metadata = g_meta
                items = g_items
                extracted_text = f"Multimodal AI Analysis ({len(items)} parameters extracted by Gemini Vision)"

        # 2. Local Deep Learning & Trained Machine Learning Pipeline
        if not items:
            if ext == "csv":
                metadata, items = extraction_service.extract_from_csv(file_bytes, filename)
                extracted_text = f"Structured CSV data with {len(items)} records."
            elif ext == "pdf":
                extracted_text, tables = pdf_service.extract_text_and_tables(file_bytes)
                if tables:
                    metadata, items = extraction_service.extract_from_tables(tables, filename, file_type="PDF", header_text=extracted_text)
                
                # If tables yielded no parameters or few parameters, run trained ML model on text
                if not items or len(items) < 3:
                    text_meta, text_items = extraction_service.extract_from_text(extracted_text, filename, file_type="PDF")
                    if text_items:
                        items = text_items
                        if not metadata or not metadata.patient_name:
                            metadata = text_meta
            else:  # PNG, JPG, JPEG Images
                ocr_boxes = ocr_service.extract_lines_and_boxes(file_bytes)
                extracted_text = "\n".join([b["text"] for b in ocr_boxes if b.get("text")])
                metadata, items = extraction_service.extract_from_ocr_lines(
                    ocr_boxes, filename, file_type=f"Image ({ext.upper()})"
                )

        # Classify items deterministically against reference intervals
        classified_items = classification_service.classify_all(items)

        # Attach evidence-based plain language medical explanations
        explained_items = medical_explanation_service.attach_explanations(classified_items)

        # Generate overall summary & outcomes
        summary = classification_service.generate_overall_summary(explained_items)

        has_uncertain = any(item.needs_verification for item in explained_items)

        return AnalysisResponse(
            metadata=metadata or ReportMetadata(filename=filename, file_type=ext.upper()),
            summary=summary,
            parameters=explained_items,
            extracted_raw_text=extracted_text[:2000] if extracted_text else "",
            has_uncertain_values=has_uncertain,
            disclaimer=MEDICAL_DISCLAIMER,
        )

    except ValueError as ve:
        logger.error(f"Validation error in file processing: {ve}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error in file processing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze report: {str(e)}")


@app.post("/api/analyze/verify-and-finalize", response_model=AnalysisResponse)
async def verify_and_finalize(payload: VerifyAndFinalizeRequest):
    """
    Called when a user confirms or corrects extracted test names, values, units, or reference intervals.
    """
    try:
        # Re-classify all items with verified user inputs
        classified_items = classification_service.classify_all(payload.parameters)
        explained_items = medical_explanation_service.attach_explanations(classified_items)
        summary = classification_service.generate_overall_summary(explained_items)

        has_uncertain = any(item.needs_verification for item in explained_items)

        return AnalysisResponse(
            metadata=payload.metadata,
            summary=summary,
            parameters=explained_items,
            extracted_raw_text="",
            has_uncertain_values=has_uncertain,
            disclaimer=MEDICAL_DISCLAIMER,
        )
    except Exception as e:
        logger.error(f"Error finalizing verified report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to finalize verified report: {str(e)}")


@app.post("/api/analyze/correlate-conditions", response_model=List[AssociatedCondition])
async def correlate_conditions_endpoint(payload: CorrelateConditionsRequest):
    """
    Dynamically correlate blood test items and active/selected symptoms with clinical conditions.
    """
    try:
        classified_items = classification_service.classify_all(payload.parameters)
        explained_items = medical_explanation_service.attach_explanations(classified_items)
        return classification_service.condition_service.correlate(
            parameters=explained_items,
            selected_symptoms=payload.selected_symptoms,
        )
    except Exception as e:
        logger.error(f"Error correlating conditions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to correlate conditions: {str(e)}")


@app.post("/api/export/csv")
async def export_csv(payload: AnalysisResponse):
    """
    Generate downloadable CSV file from actual analysis results.
    """
    csv_bytes = report_service.generate_csv_bytes(payload)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=VitalScan_{payload.metadata.filename}.csv"}
    )


@app.post("/api/export/pdf")
async def export_pdf(payload: AnalysisResponse):
    """
    Generate downloadable PDF report from actual analysis results using ReportLab.
    """
    pdf_bytes = report_service.generate_pdf_bytes(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=VitalScan_{payload.metadata.filename}.pdf"}
    )
# =====================================================================
# Serve Frontend Static Build (Production Unified Full-Stack)
# =====================================================================
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if not FRONTEND_DIST.exists():
    FRONTEND_DIST = Path("frontend/dist").resolve()

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    logger.info(f"Mounting unified production frontend from {FRONTEND_DIST}")
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa_frontend(full_path: str):
        if full_path.startswith("api") or full_path in ["docs", "openapi.json", "redoc"]:
            raise HTTPException(status_code=404, detail="API route not found")
        
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
