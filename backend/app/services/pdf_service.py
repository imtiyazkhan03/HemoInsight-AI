import io
import logging
from typing import Tuple, List, Optional
import pymupdf
from .ocr_service import OCRService

logger = logging.getLogger(__name__)


class PDFService:
    def __init__(self, ocr_service: Optional[OCRService] = None):
        self.ocr_service = ocr_service or OCRService()

    def extract_text_and_tables(self, pdf_bytes: bytes) -> Tuple[str, List[List[List[str]]]]:
        """
        Extract text and structured tables from PDF pages using PyMuPDF.
        If pages have minimal text, fall back to OCR.
        """
        extracted_text_blocks = []
        extracted_tables = []

        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            for page_idx, page in enumerate(doc):
                # Check for structured tables first
                try:
                    tables = page.find_tables()
                    for t in tables:
                        t_data = t.extract()
                        if t_data and len(t_data) > 1:
                            extracted_tables.append(t_data)
                except Exception as te:
                    logger.debug(f"Table finder notice on page {page_idx}: {te}")

                # Extract text
                text = page.get_text("text")
                if text and len(text.strip()) > 30:
                    extracted_text_blocks.append(text)
                else:
                    # Minimal text: render page to image for OCR
                    logger.info(f"Page {page_idx + 1} has sparse text. Rendering image for OCR.")
                    pix = page.get_pixmap(dpi=200)
                    img_bytes = pix.tobytes("png")
                    ocr_text = self.ocr_service.extract_text_from_image_bytes(img_bytes)
                    if ocr_text:
                        extracted_text_blocks.append(ocr_text)

            combined_text = "\n\n".join(extracted_text_blocks)
            return combined_text, extracted_tables
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            raise RuntimeError(f"Failed to process PDF: {str(e)}")
