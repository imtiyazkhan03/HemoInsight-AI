export type TestStatus = 'WITHIN_RANGE' | 'LOW' | 'HIGH' | 'NEEDS_REVIEW';

export type OverallOutcome = 'NO_ABNORMAL_DETECTED' | 'SOME_NEED_ATTENTION' | 'INSUFFICIENT_DATA';

export type ExtractionConfidence = 'HIGH' | 'MEDIUM' | 'LOW';

export interface BloodTestItem {
  id: string;
  test_name: string;
  raw_name?: string | null;
  category?: string | null;
  value?: number | null;
  raw_value?: string | null;
  unit?: string | null;
  ref_min?: number | null;
  ref_max?: number | null;
  ref_range_text?: string | null;
  lab_flag?: string | null;
  status: TestStatus;
  confidence: ExtractionConfidence;
  needs_verification: boolean;
  verification_reason?: string | null;
  explanation?: string | null;
  description?: string | null;
  questions_for_doctor: string[];
  symptoms?: string[];
}

export interface ReportMetadata {
  filename: string;
  file_type: string;
  patient_name?: string | null;
  collection_date?: string | null;
  lab_name?: string | null;
}

export interface ReportSummary {
  total_parameters: intNumber;
  within_range_count: intNumber;
  low_count: intNumber;
  high_count: intNumber;
  needs_review_count: intNumber;
  affected_parameters: string[];
  patient_symptoms?: string[];
  overall_outcome: OverallOutcome;
  overall_title: string;
  overall_message: string;
  ai_general_summary: string;
}

type intNumber = number;

export interface AnalysisResponse {
  metadata: ReportMetadata;
  summary: ReportSummary;
  parameters: BloodTestItem[];
  extracted_raw_text?: string | null;
  has_uncertain_values: boolean;
  disclaimer: string;
}

export interface SampleReport {
  id: string;
  title: string;
  description: string;
  outcome_preview: string;
  filename: string;
  parameters: BloodTestItem[];
}
