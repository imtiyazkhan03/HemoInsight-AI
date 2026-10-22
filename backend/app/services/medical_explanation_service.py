import os
import json
import logging
from pathlib import Path
from typing import List, Optional
from ..models.schemas import BloodTestItem, TestStatus

logger = logging.getLogger(__name__)

KNOWLEDGE_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "reference_ranges.json"


class MedicalExplanationService:
    def __init__(self):
        self.knowledge = {}
        if KNOWLEDGE_PATH.exists():
            try:
                with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load medical knowledge base: {e}")

        # Check if Google Gemini or OpenAI API keys are configured
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    def get_standard_explanation(self, item: BloodTestItem) -> str:
        """
        Generate evidence-supported, cautious, plain-language explanation from the knowledge base.
        """
        from .extraction_service import ExtractionService
        if not hasattr(self, "_extractor"):
            self._extractor = ExtractionService()
        _, matched_data = self._extractor.find_canonical_match(item.test_name)
        if not matched_data and item.raw_name:
            _, matched_data = self._extractor.find_canonical_match(item.raw_name)

        unit_str = f" {item.unit}" if item.unit else ""
        range_str = f" (reference: {item.ref_min} - {item.ref_max}{unit_str})" if item.ref_min is not None and item.ref_max is not None else ""

        if item.status == TestStatus.WITHIN_RANGE:
            return (
                f"Your {item.test_name} result of {item.value}{unit_str} is within the laboratory's reference interval{range_str}. "
                "This indicates that this specific parameter is behaving as expected for standard baseline screening."
            )

        if item.status == TestStatus.LOW:
            if matched_data and "low_explanation" in matched_data:
                return (
                    f"Your {item.test_name} result of {item.value}{unit_str} is below the supplied reference range{range_str}. "
                    f"{matched_data['low_explanation']} "
                    "This finding alone cannot establish any diagnosis. A healthcare professional can interpret it in light of your symptoms and full medical background."
                )
            else:
                return (
                    f"Your {item.test_name} result of {item.value}{unit_str} is below the reported reference interval{range_str}. "
                    "A lower-than-expected result can occur for various physiological, nutritional, or temporary reasons. "
                    "This individual value is not a standalone diagnosis; please review it with your physician."
                )

        if item.status == TestStatus.HIGH:
            if matched_data and "high_explanation" in matched_data:
                return (
                    f"Your {item.test_name} result of {item.value}{unit_str} is above the supplied reference range{range_str}. "
                    f"{matched_data['high_explanation']} "
                    "Elevated values should not automatically be assumed to represent a severe condition. Discuss this finding with your doctor to determine appropriate next steps or follow-up testing."
                )
            else:
                return (
                    f"Your {item.test_name} result of {item.value}{unit_str} is above the reported reference interval{range_str}. "
                    "Mild elevations can stem from dehydration, physical exertion, dietary timing, or acute reactive changes. "
                    "A healthcare provider can evaluate whether this requires monitoring or further testing."
                )

        # Status: NEEDS_REVIEW
        return (
            f"The result for {item.test_name} ({item.raw_value or 'Not detected'}) requires manual verification because "
            f"{item.verification_reason or 'the reference range or numeric reading could not be reliably established from the report'}. "
            "Please check the original paper report or consult your healthcare provider for an authoritative interpretation."
        )

    def attach_explanations(self, items: List[BloodTestItem]) -> List[BloodTestItem]:
        """
        Attaches plain-language explanations to every item in the report.
        """
        for item in items:
            item.explanation = self.get_standard_explanation(item)
            
            # Match symptoms and questions for doctor from knowledge base
            data = None
            from .extraction_service import ExtractionService
            if not hasattr(self, "_extractor"):
                self._extractor = ExtractionService()
            _, data = self._extractor.find_canonical_match(item.test_name)
            if not data and item.raw_name:
                _, data = self._extractor.find_canonical_match(item.raw_name)

            if data and not item.description:
                item.description = data.get("description")

            # Attach clinical symptoms for the person to review
            if item.status == TestStatus.LOW:
                if data and data.get("low_symptoms"):
                    item.symptoms = list(data["low_symptoms"])
                else:
                    item.symptoms = [f"Symptoms associated with low {item.test_name}; consult your physician."]
            elif item.status == TestStatus.HIGH:
                if data and data.get("high_symptoms"):
                    item.symptoms = list(data["high_symptoms"])
                else:
                    item.symptoms = [f"Symptoms associated with elevated {item.test_name}; consult your physician."]
            else:
                item.symptoms = []

            if item.status == TestStatus.WITHIN_RANGE:
                item.questions_for_doctor = [
                    f"What lifestyle or dietary habits help maintain this healthy {item.test_name} level?",
                    "Does this baseline result correlate well with my historical blood panels?"
                ]
            elif not item.questions_for_doctor:
                if data and data.get("questions_for_doctor"):
                    item.questions_for_doctor = data.get("questions_for_doctor")
                else:
                    item.questions_for_doctor = [
                        f"Could temporary factors such as hydration, diet, or recent activity explain this {item.test_name} result?",
                        "Would you recommend repeat testing or complementary laboratory markers?"
                    ]

        return items
