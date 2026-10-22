"""
Gemini Multimodal Vision AI Service for Clinical Blood Report Extraction.
Uses Google GenAI SDK (gemini-2.5-flash / gemini-2.0-flash) to extract structured
laboratory parameters, values, reference ranges, and patient metadata from PDFs and images.
"""

import os
import json
import uuid
import logging
from typing import List, Tuple, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..models.schemas import BloodTestItem, ReportMetadata, ExtractionConfidence, TestStatus

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    genai_available = True
except ImportError:
    genai = None
    types = None
    genai_available = False


class ExtractedItemSchema(BaseModel):
    test_name: str
    observed_value: Optional[float] = None
    raw_value: Optional[str] = None
    unit: Optional[str] = None
    ref_min: Optional[float] = None
    ref_max: Optional[float] = None
    ref_range_text: Optional[str] = None
    lab_flag: Optional[str] = None
    category: Optional[str] = "Laboratory Investigation"


class ExtractedReportSchema(BaseModel):
    patient_name: Optional[str] = None
    collection_date: Optional[str] = None
    lab_name: Optional[str] = None
    parameters: List[ExtractedItemSchema] = Field(default_factory=list)


class GeminiVisionService:
    def __init__(self):
        self.default_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.is_available = genai_available

    def is_configured(self, custom_key: Optional[str] = None) -> bool:
        return self.is_available and bool(custom_key or self.default_api_key)

    def extract_from_media(
        self,
        file_bytes: bytes,
        mime_type: str,
        filename: str,
        api_key: Optional[str] = None
    ) -> Tuple[bool, Optional[ReportMetadata], List[BloodTestItem], str]:
        """
        Extract blood test items using Gemini Multimodal Vision AI.
        Returns: (success, metadata, items, message)
        """
        active_key = api_key or self.default_api_key
        if not active_key:
            return False, None, [], "Gemini API key is not configured."

        if not self.is_available or genai is None or types is None:
            return False, None, [], "google-genai SDK is not installed."

        try:
            client = genai.Client(api_key=active_key)

            # Map mime_type
            if mime_type.lower() in ["jpg", "jpeg"]:
                actual_mime = "image/jpeg"
            elif mime_type.lower() == "png":
                actual_mime = "image/png"
            elif mime_type.lower() == "pdf" or mime_type.lower() == "application/pdf":
                actual_mime = "application/pdf"
            else:
                actual_mime = mime_type

            part = types.Part.from_bytes(data=file_bytes, mime_type=actual_mime)

            prompt = (
                "You are an expert clinical laboratory document parser. "
                "Analyze this blood test report image/document and extract ALL blood test investigations into JSON. "
                "For each test parameter, extract: "
                "- test_name: canonical investigation name (e.g. Hemoglobin, White Blood Cell Count, Serum Creatinine) "
                "- observed_value: numeric value as a float (e.g. 14.2) "
                "- raw_value: verbatim string as printed "
                "- unit: unit of measurement (e.g. g/dL, mg/dL, x10^3/mcL, %, fL) "
                "- ref_min: lower bound of biological reference interval as float, or null if none "
                "- ref_max: upper bound of biological reference interval as float, or null if none "
                "- ref_range_text: verbatim reference range string as printed (e.g. '12.0 - 16.0' or '< 200') "
                "- lab_flag: any abnormal flag printed by the lab (e.g. HIGH, LOW, NORMAL, H, L, *) "
                "- category: panel category (e.g. Complete Blood Count (CBC), Metabolic Panel, Lipid Profile, Liver Function) "
                "Also extract patient_name, collection_date, and lab_name if visible in the document."
            )

            # Models priority: gemini-2.5-flash or gemini-2.0-flash
            model_names = ["gemini-2.5-flash", "gemini-2.0-flash"]
            response = None
            last_err = None

            for m_name in model_names:
                try:
                    response = client.models.generate_content(
                        model=m_name,
                        contents=[part, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ExtractedReportSchema,
                            temperature=0.1,
                        )
                    )
                    if response and response.text:
                        break
                except Exception as ex:
                    last_err = ex
                    logger.warning(f"Gemini model {m_name} failed: {ex}. Retrying next model if available.")

            if not response or not response.text:
                return False, None, [], f"Gemini extraction failed: {str(last_err)}"

            parsed_data = json.loads(response.text)
            
            metadata = ReportMetadata(
                filename=filename,
                file_type=f"Document ({mime_type.upper()})",
                patient_name=parsed_data.get("patient_name"),
                collection_date=parsed_data.get("collection_date"),
                lab_name=parsed_data.get("lab_name"),
            )

            items: List[BloodTestItem] = []
            for p in parsed_data.get("parameters", []):
                val = p.get("observed_value")
                ref_min = p.get("ref_min")
                ref_max = p.get("ref_max")

                needs_verification = False
                verification_reason = None
                confidence = ExtractionConfidence.HIGH

                if val is None:
                    confidence = ExtractionConfidence.LOW
                    needs_verification = True
                    verification_reason = "Observed value was not parsed as a valid numeric reading."
                elif ref_min is None and ref_max is None:
                    confidence = ExtractionConfidence.MEDIUM
                    needs_verification = True
                    verification_reason = "No reference interval detected in document."

                item = BloodTestItem(
                    id=str(uuid.uuid4())[:8],
                    test_name=p.get("test_name", "Unknown Test"),
                    raw_name=p.get("test_name"),
                    category=p.get("category") or "General Laboratory",
                    value=val,
                    raw_value=p.get("raw_value") or (str(val) if val is not None else None),
                    unit=p.get("unit"),
                    ref_min=ref_min,
                    ref_max=ref_max,
                    ref_range_text=p.get("ref_range_text"),
                    lab_flag=p.get("lab_flag"),
                    status=TestStatus.NEEDS_REVIEW,
                    confidence=confidence,
                    needs_verification=needs_verification,
                    verification_reason=verification_reason,
                )
                items.append(item)

            logger.info(f"Gemini Vision successfully extracted {len(items)} blood test parameters.")
            return True, metadata, items, f"Extracted {len(items)} parameters via Gemini Multimodal Vision AI."

        except Exception as e:
            logger.error(f"Error in Gemini Vision extraction: {e}")
            return False, None, [], f"Gemini Vision extraction error: {str(e)}"
