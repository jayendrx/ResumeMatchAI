"""Text preprocessing module for resume and job description text."""

import re


def preprocess_text(text: str) -> str:
    """Preprocess text for NLP analysis.

    Performs light cleaning while preserving important technical terms,
    programming languages, abbreviations, and numbers.

    Args:
        text: Raw input text.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ''

    # Normalize unicode
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)

    # Remove email addresses
    text = re.sub(r'\S+@\S+\.\S+', '', text)

    # Remove phone numbers (various formats)
    text = re.sub(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}', '', text)

    # Normalize whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove special characters but keep those relevant to tech terms
    # Keep: letters, numbers, +, #, ., -, /, @, spaces, newlines
    text = re.sub(r"[^a-zA-Z0-9\s\+\#\.\-\/\,\(\)\'\:]", ' ', text)

    # Normalize whitespace again after cleaning
    text = re.sub(r'[ \t]+', ' ', text)

    # Clean up lines
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    text = '\n'.join(cleaned_lines)

    return text.strip()


def extract_sections(text: str) -> dict:
    """Attempt to extract common resume sections.

    Args:
        text: Resume text.

    Returns:
        Dictionary mapping section names to their content.
    """
    section_headers = [
        'summary', 'objective', 'professional summary', 'profile',
        'experience', 'work experience', 'professional experience', 'employment',
        'education', 'academic', 'qualifications',
        'skills', 'technical skills', 'core competencies', 'competencies',
        'projects', 'personal projects', 'academic projects',
        'certifications', 'certificates', 'licenses',
        'publications', 'research',
        'awards', 'achievements', 'honors',
        'languages', 'interests', 'hobbies',
        'references', 'volunteer', 'volunteering',
    ]

    # Build regex pattern for section headers
    pattern = r'^\s*(' + '|'.join(re.escape(h) for h in section_headers) + r')\s*[:.]?\s*$'

    sections = {}
    current_section = 'header'
    current_content = []

    for line in text.split('\n'):
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = match.group(1).strip().lower()
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()

    return sections
