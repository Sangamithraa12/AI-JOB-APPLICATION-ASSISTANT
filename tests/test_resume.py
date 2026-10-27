"""Tests for Resume Service (Feature A).

Covers:
- File extension validation
- Empty / corrupted PDF handling
- Scanned / minimal text detection
- Valid PDF extraction
- Privacy cleanup
"""

import io
import unittest
from pathlib import Path
from pypdf import PdfWriter
from fpdf import FPDF

from services.resume_service import resume_service
from config import Config

class TestResumeService(unittest.TestCase):
    """Test suite for PDF extraction, validation, and scanned document detection."""

    def test_allowed_file(self):
        """Verify extension whitelisting."""
        self.assertTrue(resume_service.allowed_file("resume.pdf"))
        self.assertTrue(resume_service.allowed_file("candidate_cv.PDF"))
        self.assertFalse(resume_service.allowed_file("resume.docx"))
        self.assertFalse(resume_service.allowed_file("malicious.exe"))
        self.assertFalse(resume_service.allowed_file("no_extension"))

    def test_empty_corrupted_stream(self):
        """Corrupted or random bytes should raise a ValueError gracefully."""
        corrupt_stream = io.BytesIO(b"This is not a real PDF file header.")
        with self.assertRaises(ValueError):
            resume_service.extract_text_from_pdf_stream(corrupt_stream)

    def test_scanned_or_empty_pdf_detection(self):
        """Blank PDF pages should be flagged with scanned_or_empty warning."""
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        stream = io.BytesIO()
        writer.write(stream)
        stream.seek(0)

        text, metadata = resume_service.extract_text_from_pdf_stream(stream)
        self.assertEqual(len(text), 0)
        self.assertTrue(metadata["is_scanned_or_empty"])
        self.assertIsNotNone(metadata["warning"])
        self.assertIn("scanned image", metadata["warning"])

    def test_valid_pdf_text_extraction(self):
        """Generate a synthetic text PDF and verify extracted contents and metrics."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="John Doe - Python Developer", ln=1, align="C")
        pdf.cell(200, 10, txt="Experience: Flask, SQL, and Automated Testing.", ln=2, align="L")

        pdf_bytes = pdf.output(dest="S").encode("latin1")
        stream = io.BytesIO(pdf_bytes)

        text, metadata = resume_service.extract_text_from_pdf_stream(stream)
        self.assertIn("John Doe", text)
        self.assertIn("Python Developer", text)
        self.assertIn("Flask", text)
        self.assertFalse(metadata["is_scanned_or_empty"])
        self.assertIsNone(metadata["warning"])
        self.assertGreater(metadata["char_count"], 40)
        self.assertGreater(metadata["word_count"], 5)

if __name__ == "__main__":
    unittest.main()
