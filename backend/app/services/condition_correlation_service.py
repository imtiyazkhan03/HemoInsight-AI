import json
import logging
from pathlib import Path
from typing import List, Optional
from ..models.schemas import BloodTestItem, TestStatus, AssociatedCondition

logger = logging.getLogger(__name__)

PATTERNS_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "condition_patterns.json"


class ConditionCorrelationService:
    def __init__(self):
        self.patterns = []
        if PATTERNS_PATH.exists():
            try:
                with open(PATTERNS_PATH, "r", encoding="utf-8") as f:
                    self.patterns = json.load(f)
                logger.info(f"Loaded {len(self.patterns)} clinical condition correlation patterns.")
            except Exception as e:
                logger.error(f"Failed to load condition patterns: {e}")

    def correlate(
        self,
        parameters: List[BloodTestItem],
        selected_symptoms: Optional[List[str]] = None,
    ) -> List[AssociatedCondition]:
        """
        Correlate laboratory biomarker findings and reported clinical symptoms
        against established clinical patterns.
        """
        if not self.patterns or not parameters:
            return []

        # Collect active symptoms: either user-selected, or derived from abnormal parameters
        active_symptoms = set()
        if selected_symptoms:
            for s in selected_symptoms:
                if s and s.strip():
                    active_symptoms.add(s.strip().lower())
        else:
            for item in parameters:
                if item.status in [TestStatus.LOW, TestStatus.HIGH] and item.symptoms:
                    for s in item.symptoms:
                        active_symptoms.add(s.lower())

        results: List[AssociatedCondition] = []

        for pattern in self.patterns:
            matched_biomarkers = []
            matched_symptoms = []
            biomarker_points = 0.0
            max_biomarker_points = 0.0
            characteristic_matched = 0

            # 1. Evaluate Biomarker Rules
            for rule in pattern.get("biomarker_rules", []):
                weight = float(rule.get("weight", 1.0))
                max_biomarker_points += weight
                keys = [k.lower() for k in rule.get("parameter_keys", [])]
                expected_status = rule.get("expected_status")

                # Find any parameter matching keys
                found_match = False
                for p in parameters:
                    name_lower = (p.test_name or "").lower()
                    raw_lower = (p.raw_name or "").lower()

                    matches_key = any(k in name_lower or k in raw_lower for k in keys)
                    if matches_key:
                        actual_status = p.status.value if hasattr(p.status, "value") else str(p.status)
                        if actual_status == expected_status:
                            val_str = f" ({p.value} {p.unit})" if p.value is not None and p.unit else ""
                            desc = rule.get("description", f"{p.test_name} {actual_status}")
                            matched_biomarkers.append(f"{desc}{val_str}")
                            biomarker_points += weight
                            if rule.get("importance") == "characteristic":
                                characteristic_matched += 1
                            found_match = True
                            break

            # 2. Evaluate Clinical Symptoms
            symptom_keywords = [k.lower() for k in pattern.get("symptom_keywords", [])]
            for sym in active_symptoms:
                for kw in symptom_keywords:
                    if kw in sym:
                        # Add readable symptom phrase
                        formatted_sym = sym.capitalize()
                        if formatted_sym not in matched_symptoms:
                            matched_symptoms.append(formatted_sym)
                        break

            # Only consider conditions where at least one biomarker matched
            if not matched_biomarkers:
                continue

            # Calculate match score (0 - 100)
            biomarker_ratio = biomarker_points / max_biomarker_points if max_biomarker_points > 0 else 0
            symptom_bonus = min(len(matched_symptoms) * 10, 30)

            # Raw score based on weighted biomarkers (70% weight) + symptoms (30% weight)
            calculated_score = int((biomarker_ratio * 70) + symptom_bonus)

            # Boost if characteristic biomarker was matched
            if characteristic_matched >= 2:
                calculated_score = min(calculated_score + 15, 98)
            elif characteristic_matched == 1 and biomarker_ratio >= 0.5:
                calculated_score = min(calculated_score + 10, 95)

            # Minimum threshold to display
            if calculated_score < 25:
                continue

            if calculated_score >= 70:
                match_level = "High Correlation"
            elif calculated_score >= 45:
                match_level = "Moderate Correlation"
            else:
                match_level = "Possible Consideration"

            results.append(
                AssociatedCondition(
                    id=pattern.get("id", "condition"),
                    condition_name=pattern.get("condition_name", "Clinical Condition"),
                    category=pattern.get("category", "General Medicine"),
                    severity_level=pattern.get("severity_level", "Clinical Follow-up Recommended"),
                    match_level=match_level,
                    match_score=calculated_score,
                    matching_biomarkers=matched_biomarkers,
                    matching_symptoms=matched_symptoms[:4],
                    overview=pattern.get("overview", ""),
                    suggested_follow_up_tests=pattern.get("suggested_follow_up_tests", []),
                    doctor_discussion_points=pattern.get("doctor_discussion_points", []),
                )
            )

        # Sort by match_score descending, limit to top 5
        results.sort(key=lambda c: c.match_score, reverse=True)
        return results[:5]
