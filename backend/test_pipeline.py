import os
import io
from backend.app.services.extraction_service import ExtractionService
from backend.app.services.pdf_service import PDFService
from backend.app.services.classification_service import ClassificationService
from backend.app.services.medical_explanation_service import MedicalExplanationService
from backend.app.services.report_service import ReportService
from backend.app.models.schemas import TestStatus, OverallOutcome, AnalysisResponse, ReportMetadata

def test_pipeline():
    pdf_service = PDFService()
    extraction_service = ExtractionService()
    classification_service = ClassificationService()
    medical_explanation_service = MedicalExplanationService()
    report_service = ReportService()

    samples_dir = os.path.join(os.path.dirname(__file__), "app", "samples")
    pdf_path = os.path.join(samples_dir, "sample_cbc_anemia.pdf")
    csv_path = os.path.join(samples_dir, "sample_routine_checkup.csv")

    # 1. Test PDF
    print("--- Testing PDF Extraction & Classification ---")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    text, tables = pdf_service.extract_text_and_tables(pdf_bytes)
    print(f"Extracted PDF text length: {len(text)} chars, tables found: {len(tables)}")
    if tables:
        metadata, items = extraction_service.extract_from_tables(tables, "sample_cbc_anemia.pdf", file_type="PDF", header_text=text)
    else:
        metadata, items = extraction_service.extract_from_text(text, "sample_cbc_anemia.pdf", file_type="PDF")
    print(f"Extracted {len(items)} parameters from PDF")
    for item in items:
        print(f"  > {item.test_name}: {item.value} {item.unit} (Ref: {item.ref_min}-{item.ref_max})")

    classified_items = classification_service.classify_all(items)
    explained_items = medical_explanation_service.attach_explanations(classified_items)
    summary = classification_service.generate_overall_summary(explained_items)

    print(f"Overall Outcome: {summary.overall_outcome}")
    print(f"Outcome Title: {summary.overall_title}")
    print(f"Low count: {summary.low_count}, Within range: {summary.within_range_count}, High count: {summary.high_count}")
    assert summary.overall_outcome == OverallOutcome.SOME_NEED_ATTENTION, "Expected SOME_NEED_ATTENTION"
    print("PDF Test PASSED!\n")

    # 2. Test CSV
    print("--- Testing CSV Extraction & Classification ---")
    with open(csv_path, "rb") as f:
        csv_bytes = f.read()

    meta_csv, items_csv = extraction_service.extract_from_csv(csv_bytes, "sample_routine_checkup.csv")
    classified_csv = classification_service.classify_all(items_csv)
    explained_csv = medical_explanation_service.attach_explanations(classified_csv)
    summary_csv = classification_service.generate_overall_summary(explained_csv)

    print(f"Overall Outcome: {summary_csv.overall_outcome}")
    print(f"Within range: {summary_csv.within_range_count}/{summary_csv.total_parameters}")
    assert summary_csv.overall_outcome == OverallOutcome.NO_ABNORMAL_DETECTED, "Expected NO_ABNORMAL_DETECTED"
    print("CSV Test PASSED!\n")

    # 3. Test Exports
    print("--- Testing PDF and CSV Report Generation ---")
    resp = AnalysisResponse(
        metadata=meta_csv,
        summary=summary_csv,
        parameters=explained_csv,
        extracted_raw_text="",
        has_uncertain_values=False,
        disclaimer="Academic disclaimer."
    )
    generated_pdf = report_service.generate_pdf_bytes(resp)
    assert len(generated_pdf) > 1000, "Generated PDF is too small"
    generated_csv = report_service.generate_csv_bytes(resp)
    assert len(generated_csv) > 100, "Generated CSV is too small"
    print("Export Tests PASSED! (PDF bytes:", len(generated_pdf), ", CSV bytes:", len(generated_csv), ")")

if __name__ == "__main__":
    test_pipeline()
