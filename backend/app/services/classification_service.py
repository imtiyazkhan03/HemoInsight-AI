import logging
from typing import List, Tuple, Optional
from ..models.schemas import BloodTestItem, TestStatus, ReportSummary, OverallOutcome
from .condition_correlation_service import ConditionCorrelationService

logger = logging.getLogger(__name__)


class ClassificationService:
    def __init__(self):
        self.condition_service = ConditionCorrelationService()
    def classify_item(self, item: BloodTestItem) -> BloodTestItem:
        """
        Classifies an individual blood test item according to verified values and reference ranges.
        """
        # Check if value is present and valid
        if item.value is None:
            item.status = TestStatus.NEEDS_REVIEW
            item.needs_verification = True
            if not item.verification_reason:
                item.verification_reason = "Missing numerical value."
            return item

        # Check reference range boundaries
        if item.ref_min is None or item.ref_max is None:
            item.status = TestStatus.NEEDS_REVIEW
            item.needs_verification = True
            if not item.verification_reason:
                item.verification_reason = "Missing laboratory reference interval."
            return item

        # Classify
        val = float(item.value)
        min_val = float(item.ref_min)
        max_val = float(item.ref_max)

        if val < min_val:
            item.status = TestStatus.LOW
        elif val > max_val:
            item.status = TestStatus.HIGH
        else:
            item.status = TestStatus.WITHIN_RANGE

        return item

    def classify_all(self, items: List[BloodTestItem]) -> List[BloodTestItem]:
        """
        Classify all items in the report.
        """
        return [self.classify_item(item) for item in items]

    def generate_overall_summary(
        self,
        items: List[BloodTestItem],
        selected_symptoms: Optional[List[str]] = None,
    ) -> ReportSummary:
        """
        Calculates report-level statistics and determines overall outcome (Outcome A, B, or C).
        """
        total = len(items)
        within_range = sum(1 for item in items if item.status == TestStatus.WITHIN_RANGE)
        low_count = sum(1 for item in items if item.status == TestStatus.LOW)
        high_count = sum(1 for item in items if item.status == TestStatus.HIGH)
        needs_review = sum(1 for item in items if item.status == TestStatus.NEEDS_REVIEW)

        affected_params = [
            f"{item.test_name} ({'Low' if item.status == TestStatus.LOW else 'High'})"
            for item in items
            if item.status in [TestStatus.LOW, TestStatus.HIGH]
        ]

        # Aggregate and deduplicate clinical symptoms reported for the person to review
        patient_symptoms = []
        seen_symptoms = set()
        for item in items:
            if item.status in [TestStatus.LOW, TestStatus.HIGH] and item.symptoms:
                for symp in item.symptoms:
                    clean_s = symp.strip()
                    if clean_s and clean_s.lower() not in seen_symptoms:
                        seen_symptoms.add(clean_s.lower())
                        patient_symptoms.append(clean_s)

        # Correlate biomarkers and symptoms with clinical condition patterns
        associated_conditions = self.condition_service.correlate(
            parameters=items,
            selected_symptoms=selected_symptoms or patient_symptoms
        )

        # Determine Outcome
        if total == 0 or (needs_review > 0 and needs_review >= total / 2):
            outcome = OverallOutcome.INSUFFICIENT_DATA
            title = "Unable to Fully Analyze This Report"
            msg = "Some laboratory values or reference ranges could not be extracted or verified. Please review the extracted information or upload a clearer report."
            ai_summary = "Crucial test parameters or reference ranges were absent or ambiguous. Incomplete data cannot be verified as normal. Please verify the highlighted items in the review table."
        elif low_count > 0 or high_count > 0:
            outcome = OverallOutcome.SOME_NEED_ATTENTION
            title = "Some Results Need Attention"
            msg = "We detected one or more values outside the supplied laboratory reference ranges. Review the flagged results below to understand what they may indicate and what to discuss with a healthcare professional."
            ai_summary = f"{len(affected_params)} test result(s) were found outside their laboratory reference ranges: {', '.join(affected_params)}. Review the plain-language explanations below and share these findings with your healthcare provider."
        else:
            outcome = OverallOutcome.NO_ABNORMAL_DETECTED
            title = "No Out-of-Range Results Detected"
            msg = "All successfully analyzed values fall within their supplied reference ranges. This does not guarantee that every aspect of your health is normal, and the findings should be considered alongside symptoms and medical history."
            ai_summary = f"All {within_range} analyzed parameters were within the laboratory's reported reference boundaries. While this is encouraging, laboratory reference intervals are screening baselines and should always be viewed in the context of your overall health and clinical presentation."

        return ReportSummary(
            total_parameters=total,
            within_range_count=within_range,
            low_count=low_count,
            high_count=high_count,
            needs_review_count=needs_review,
            affected_parameters=affected_params,
            patient_symptoms=patient_symptoms,
            associated_conditions=associated_conditions,
            overall_outcome=outcome,
            overall_title=title,
            overall_message=msg,
            ai_general_summary=ai_summary,
        )
