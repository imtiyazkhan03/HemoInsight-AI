import pytest
from backend.app.ml.model_inference import MLInferenceEngine
from backend.app.services.extraction_service import ExtractionService
from backend.app.services.classification_service import ClassificationService
from backend.app.services.medical_explanation_service import MedicalExplanationService
from backend.app.models.schemas import TestStatus, OverallOutcome, BloodTestItem


def test_ml_model_loaded_and_high_accuracy():
    ml_engine = MLInferenceEngine.get_instance()
    assert ml_engine.is_loaded, "ML model must be successfully loaded from joblib"
    assert ml_engine.accuracy >= 0.95, f"Expected accuracy >= 95%, got {ml_engine.accuracy * 100:.2f}%"
    print(f"ML Model Token Accuracy: {ml_engine.accuracy * 100:.2f}%")


def test_ocr_line_parameter_ranging():
    ml_engine = MLInferenceEngine.get_instance()
    sample_ocr_lines = [
        "Patient: John Doe Age: 42 Y Male",
        "Apex Clinical Laboratories",
        "Hemoglobin 9.4 g/dL 12.0 - 17.5 LOW",
        "Total Cholesterol 245 mg/dL < 200 HIGH",
        "Fasting Glucose 88 mg/dL 70 - 99 NORMAL",
        "Platelet Count 95 x10^3/mcL 150 - 450 LOW",
    ]

    metadata, items = ml_engine.extract_from_lines(sample_ocr_lines)
    assert len(items) >= 4, f"Expected at least 4 items extracted, got {len(items)}"

    # Check Hemoglobin
    hb_item = next((i for i in items if "hemoglobin" in i.test_name.lower()), None)
    assert hb_item is not None, "Hemoglobin must be extracted"
    assert hb_item.value == 9.4
    assert hb_item.ref_min == 12.0
    assert hb_item.ref_max == 17.5

    # Check Cholesterol
    chol_item = next((i for i in items if "cholesterol" in i.test_name.lower()), None)
    assert chol_item is not None, "Cholesterol must be extracted"
    assert chol_item.value == 245.0
    assert chol_item.ref_max == 200.0


def test_symptoms_output_for_patient():
    classification_service = ClassificationService()
    medical_explanation_service = MedicalExplanationService()

    # Create low hemoglobin and high glucose test items
    items = [
        BloodTestItem(
            id="test-1",
            test_name="Hemoglobin",
            value=8.8,
            unit="g/dL",
            ref_min=12.0,
            ref_max=17.5,
            status=TestStatus.NEEDS_REVIEW
        ),
        BloodTestItem(
            id="test-2",
            test_name="Fasting Glucose",
            value=165.0,
            unit="mg/dL",
            ref_min=70.0,
            ref_max=99.0,
            status=TestStatus.NEEDS_REVIEW
        )
    ]

    classified = classification_service.classify_all(items)
    assert classified[0].status == TestStatus.LOW
    assert classified[1].status == TestStatus.HIGH

    explained = medical_explanation_service.attach_explanations(classified)
    
    # Verify symptoms attached to Low Hemoglobin
    assert len(explained[0].symptoms) > 0, "Low Hemoglobin must have correlated symptoms"
    assert any("fatigue" in s.lower() for s in explained[0].symptoms), "Expected fatigue in hemoglobin symptoms"

    # Verify symptoms attached to High Glucose
    assert len(explained[1].symptoms) > 0, "High Glucose must have correlated symptoms"
    assert any("thirst" in s.lower() or "urination" in s.lower() or "fatigue" in s.lower() for s in explained[1].symptoms)

    # Verify ReportSummary patient_symptoms aggregation
    summary = classification_service.generate_overall_summary(explained)
    assert summary.overall_outcome == OverallOutcome.SOME_NEED_ATTENTION
    assert len(summary.patient_symptoms) > 0, "ReportSummary must contain aggregated patient symptoms"
    print(f"Aggregated {len(summary.patient_symptoms)} patient symptoms: {summary.patient_symptoms[:3]}")
