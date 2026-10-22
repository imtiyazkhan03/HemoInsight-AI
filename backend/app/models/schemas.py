from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    __test__ = False
    WITHIN_RANGE = "WITHIN_RANGE"
    LOW = "LOW"
    HIGH = "HIGH"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class OverallOutcome(str, Enum):
    NO_ABNORMAL_DETECTED = "NO_ABNORMAL_DETECTED"
    SOME_NEED_ATTENTION = "SOME_NEED_ATTENTION"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ExtractionConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class BloodTestItem(BaseModel):
    id: str
    test_name: str
    raw_name: Optional[str] = None
    category: Optional[str] = "General Laboratory"
    value: Optional[float] = None
    raw_value: Optional[str] = None
    unit: Optional[str] = None
    ref_min: Optional[float] = None
    ref_max: Optional[float] = None
    ref_range_text: Optional[str] = None
    lab_flag: Optional[str] = None
    status: TestStatus = TestStatus.NEEDS_REVIEW
    confidence: ExtractionConfidence = ExtractionConfidence.HIGH
    needs_verification: bool = False
    verification_reason: Optional[str] = None
    explanation: Optional[str] = None
    description: Optional[str] = None
    questions_for_doctor: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)


class ReportMetadata(BaseModel):
    filename: str
    file_type: str
    patient_name: Optional[str] = None
    collection_date: Optional[str] = None
    lab_name: Optional[str] = None


class ReportSummary(BaseModel):
    total_parameters: int
    within_range_count: int
    low_count: int
    high_count: int
    needs_review_count: int
    affected_parameters: List[str] = Field(default_factory=list)
    patient_symptoms: List[str] = Field(default_factory=list)
    overall_outcome: OverallOutcome
    overall_title: str
    overall_message: str
    ai_general_summary: str


class AnalysisResponse(BaseModel):
    metadata: ReportMetadata
    summary: ReportSummary
    parameters: List[BloodTestItem]
    extracted_raw_text: Optional[str] = None
    has_uncertain_values: bool = False
    disclaimer: str


class VerifyAndFinalizeRequest(BaseModel):
    metadata: ReportMetadata
    parameters: List[BloodTestItem]


class SampleReport(BaseModel):
    id: str
    title: str
    description: str
    outcome_preview: str
    filename: str
    parameters: List[BloodTestItem]
