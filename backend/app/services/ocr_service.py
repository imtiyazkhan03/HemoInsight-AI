import io
import os
import shutil
import logging
from typing import Optional, List, Dict, Any, Tuple
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

# Check for RapidOCR (Deep learning ONNX engine)
try:
    from rapidocr_onnxruntime import RapidOCR
    rapid_ocr_available = True
except ImportError:
    RapidOCR = None
    rapid_ocr_available = False

# Try to find tesseract executable if installed
TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"),
]

try:
    import pytesseract
    if not shutil.which("tesseract"):
        for candidate in TESSERACT_CANDIDATES:
            if os.path.exists(candidate):
                pytesseract.pytesseract.tesseract_cmd = candidate
                break
except ImportError:
    pytesseract = None


class OCRService:
    def __init__(self):
        self.rapid_engine = None
        self.engine_name = "None"

        if rapid_ocr_available and RapidOCR is not None:
            try:
                self.rapid_engine = RapidOCR()
                self.engine_name = "RapidOCR (Deep Learning ONNX)"
                logger.info("Initialized RapidOCR Deep Learning engine successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize RapidOCR: {e}")

        has_tesseract = pytesseract is not None and (
            shutil.which("tesseract") is not None
            or os.path.exists(getattr(pytesseract, "tesseract_cmd", ""))
        )
        if self.rapid_engine is None and has_tesseract:
            self.engine_name = "Tesseract OCR"

        self.is_available = (self.rapid_engine is not None) or has_tesseract

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance image contrast, handle low resolutions, and sharpen to maximize OCR accuracy.
        """
        if image.mode != "RGB":
            img = image.convert("RGB")
        else:
            img = image.copy()

        # If image resolution is low, upscale to at least 1600px width/height for clear small text
        w, h = img.size
        if w < 1400 or h < 1400:
            scale = max(1400 / w, 1400 / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Gentle contrast and sharpness enhancement
        enhancer = ImageEnhance.Contrast(img)
        enhanced = enhancer.enhance(1.25)
        sharpener = ImageEnhance.Sharpness(enhanced)
        sharpened = sharpener.enhance(1.3)
        return sharpened

    def extract_lines_and_boxes(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Extract text lines with bounding boxes and detection confidence scores using Deep Learning OCR.
        Clusters horizontal bounding boxes into coherent table lines.
        """
        results = []
        try:
            image = Image.open(io.BytesIO(image_bytes))
            processed = self.preprocess_image(image)

            # Convert to RGB bytes for RapidOCR
            if self.rapid_engine:
                buf = io.BytesIO()
                processed.save(buf, format="PNG")
                ocr_output, _ = self.rapid_engine(buf.getvalue())
                if ocr_output:
                    # Spatial 2D layout reconstruction: cluster boxes by visual row
                    boxes_with_info = []
                    for box, text, score in ocr_output:
                        clean_text = text.strip()
                        if not clean_text:
                            continue
                        ys = [pt[1] for pt in box]
                        xs = [pt[0] for pt in box]
                        y_min = min(ys)
                        y_max = max(ys)
                        cy = sum(ys) / len(ys)
                        h = max(y_max - y_min, 1.0)
                        x_min = min(xs)
                        x_max = max(xs)

                        boxes_with_info.append({
                            "text": clean_text,
                            "box": box,
                            "score": float(score) if score is not None else 1.0,
                            "cy": cy,
                            "h": h,
                            "y_min": y_min,
                            "y_max": y_max,
                            "x_min": x_min,
                            "x_max": x_max,
                        })

                    # Sort top-to-bottom by vertical center
                    boxes_with_info.sort(key=lambda b: (b["cy"], b["x_min"]))

                    # Cluster boxes into lines based on vertical overlap and running center
                    clustered_lines: List[List[Dict[str, Any]]] = []
                    current_line: List[Dict[str, Any]] = []

                    for b in boxes_with_info:
                        if not current_line:
                            current_line.append(b)
                        else:
                            # Calculate line vertical properties
                            line_cy = sum(item["cy"] for item in current_line) / len(current_line)
                            line_h = max(item["h"] for item in current_line)
                            line_y_min = min(item["y_min"] for item in current_line)
                            line_y_max = max(item["y_max"] for item in current_line)

                            # Check vertical overlap
                            overlap = max(0.0, min(line_y_max, b["y_max"]) - max(line_y_min, b["y_min"]))
                            min_h = min(line_h, b["h"])
                            overlap_ratio = overlap / min_h if min_h > 0 else 0.0

                            # Determine if b belongs on this horizontal row
                            is_same_row = (abs(b["cy"] - line_cy) <= max(line_h * 0.70, 14.0)) or (overlap_ratio >= 0.35)

                            if is_same_row:
                                current_line.append(b)
                            else:
                                current_line.sort(key=lambda x: x["x_min"])
                                clustered_lines.append(current_line)
                                current_line = [b]

                    if current_line:
                        current_line.sort(key=lambda x: x["x_min"])
                        clustered_lines.append(current_line)

                    # Form clean text lines and average scores
                    for line_boxes in clustered_lines:
                        line_text = " ".join([b["text"] for b in line_boxes])
                        avg_score = sum([b["score"] for b in line_boxes]) / len(line_boxes)
                        results.append({
                            "text": line_text,
                            "box": [line_boxes[0]["box"][0], line_boxes[-1]["box"][1], line_boxes[-1]["box"][2], line_boxes[0]["box"][3]],
                            "confidence": avg_score,
                        })
                    return results

            # Fallback to pytesseract
            if pytesseract is not None and shutil.which("tesseract"):
                raw_text = pytesseract.image_to_string(processed)
                for line in raw_text.splitlines():
                    if line.strip():
                        results.append({
                            "text": line.strip(),
                            "box": None,
                            "confidence": 0.85,
                        })
                return results

        except Exception as e:
            logger.error(f"Error during OCR lines extraction: {e}")

        return results

    def extract_text_from_image_bytes(self, image_bytes: bytes) -> str:
        """
        Extract text from raw image bytes using deep learning or tesseract.
        """
        lines = self.extract_lines_and_boxes(image_bytes)
        if lines:
            return "\n".join([item["text"] for item in lines])

        if not self.is_available:
            return (
                "OCR Notice: No OCR engine is currently detected. "
                "Please upload PDF reports with embedded text or structured CSV reports."
            )

        return ""
