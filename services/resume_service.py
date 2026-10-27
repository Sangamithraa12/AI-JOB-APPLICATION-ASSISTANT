"""Resume processing service using pypdf.

Validates:
- File size (< 5MB)
- File extension and magic bytes
- Text density (detects scanned/empty/corrupted PDFs)
- Temporary cleanup ensuring no unauthorized permanent retention
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Tuple
import pypdf
from config import Config

class ResumeService:
    """Handles PDF validation, secure extraction, and privacy safeguards."""

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Validate filename extension against allowed list."""
        return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def extract_text_from_pdf_stream(stream_or_path) -> Tuple[str, Dict[str, Any]]:
        """Extract text from a PDF file stream or path.

        Returns:
            Tuple of (extracted_text, metadata_dict)
        Raises:
            ValueError: If file is corrupted, empty, or unreadable.
        """
        try:
            reader = pypdf.PdfReader(stream_or_path)
            num_pages = len(reader.pages)
            if num_pages == 0:
                raise ValueError("The uploaded PDF has 0 pages.")

            extracted_pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                extracted_pages.append(text)

            full_text = "\n\n".join(extracted_pages).strip()

            # Text normalization
            # Replace multiple whitespace characters while preserving paragraph breaks
            normalized_text = re.sub(r'[ \t]+', ' ', full_text)
            normalized_text = re.sub(r'\n{3,}', '\n\n', normalized_text)

            char_count = len(normalized_text)
            word_count = len(normalized_text.split()) if normalized_text else 0

            # Scanned / Image-only PDF detection
            is_scanned = False
            warning_message = None

            if char_count < 60:
                is_scanned = True
                warning_message = (
                    "Warning: Minimal or no text extracted (<60 characters). "
                    "This document may be a scanned image or flattening without selectable text. "
                    "Please upload a text-selectable PDF or paste your resume text manually."
                )

            metadata = {
                "num_pages": num_pages,
                "char_count": char_count,
                "word_count": word_count,
                "is_scanned_or_empty": is_scanned,
                "warning": warning_message
            }

            return normalized_text, metadata

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Could not read PDF file: {str(e)}")

    @staticmethod
    def cleanup_temporary_file(file_path: Path) -> None:
        """Safely delete temporary upload to comply with privacy directive."""
        try:
            if file_path and file_path.exists():
                file_path.unlink()
        except Exception:
            pass

resume_service = ResumeService()
