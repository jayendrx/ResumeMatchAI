"""Resume parser module for extracting text from PDF files."""

import re
from io import BytesIO
from pypdf import PdfReader


def extract_resume_text(pdf_file) -> dict:
    """Extract text from a PDF file.

    Args:
        pdf_file: A file-like object or path to a PDF file.

    Returns:
        dict with keys:
            - 'text': Extracted text string.
            - 'success': Boolean indicating success.
            - 'error': Error message if extraction failed.
            - 'page_count': Number of pages processed.
    """
    try:
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        elif hasattr(pdf_file, 'read'):
            pdf_data = pdf_file.read()
            pdf_file = BytesIO(pdf_data)

        reader = PdfReader(pdf_file)
        page_count = len(reader.pages)

        if page_count == 0:
            return {
                'text': '',
                'success': False,
                'error': 'The PDF file contains no pages.',
                'page_count': 0,
            }

        # Check if PDF is encrypted
        if reader.is_encrypted:
            try:
                reader.decrypt('')
            except Exception:
                return {
                    'text': '',
                    'success': False,
                    'error': 'The PDF is encrypted and cannot be read. Please provide an unencrypted PDF.',
                    'page_count': page_count,
                }

        all_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                all_text.append(page_text)

        full_text = '\n'.join(all_text)

        # Clean the extracted text
        full_text = _clean_extracted_text(full_text)

        if not full_text.strip():
            return {
                'text': '',
                'success': False,
                'error': (
                    'No readable text found in the PDF. '
                    'This may be an image-only or scanned PDF. '
                    'OCR is not currently supported. '
                    'Please provide a text-based PDF or paste your resume text directly.'
                ),
                'page_count': page_count,
            }

        return {
            'text': full_text,
            'success': True,
            'error': None,
            'page_count': page_count,
        }

    except Exception as e:
        return {
            'text': '',
            'success': False,
            'error': f'Failed to read the PDF file: {str(e)}',
            'page_count': 0,
        }


def _clean_extracted_text(text: str) -> str:
    """Clean extracted PDF text while preserving structure."""
    # Normalize unicode characters
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u2022', '- ')

    # Normalize whitespace within lines but preserve paragraph breaks
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'[ \t]+', ' ', line).strip()
        cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Remove excessive blank lines (keep at most 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()
