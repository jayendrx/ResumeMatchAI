"""Skill extraction module using configurable taxonomy with word-boundary matching."""

import json
import os
import re
from pathlib import Path


def load_taxonomy(taxonomy_path: str = None) -> dict:
    """Load the skills taxonomy from a JSON file.

    Args:
        taxonomy_path: Optional path to taxonomy file.
                       Defaults to data/skills_taxonomy.json.

    Returns:
        Dictionary containing the skills taxonomy.
    """
    if taxonomy_path is None:
        base_dir = Path(__file__).resolve().parent.parent
        taxonomy_path = base_dir / 'data' / 'skills_taxonomy.json'

    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_skills(text: str, taxonomy: dict = None) -> dict:
    """Extract skills from text using the skills taxonomy.

    Uses case-insensitive, word-boundary-aware matching to find skills
    in the text. Also resolves aliases to canonical skill names.

    Args:
        text: Input text to extract skills from.
        taxonomy: Skills taxonomy dict. If None, loads from default path.

    Returns:
        dict with keys:
            - 'skills': Set of matched canonical skill names.
            - 'categorized': Dict mapping category -> list of skills found.
            - 'details': List of dicts with skill, category, and match info.
    """
    if not text:
        return {'skills': set(), 'categorized': {}, 'details': []}

    if taxonomy is None:
        taxonomy = load_taxonomy()

    text_lower = text.lower()
    found_skills = set()
    categorized = {}
    details = []

    for category, cat_data in taxonomy.items():
        skills_list = cat_data.get('skills', [])
        aliases = cat_data.get('aliases', {})
        category_skills = []

        # Check each skill
        for skill in skills_list:
            if _match_skill(skill, text, text_lower):
                if skill not in found_skills:
                    found_skills.add(skill)
                    category_skills.append(skill)
                    details.append({
                        'skill': skill,
                        'category': category,
                        'matched_as': skill,
                    })

        # Check aliases
        for alias, canonical in aliases.items():
            if _match_skill(alias, text, text_lower):
                if canonical not in found_skills:
                    found_skills.add(canonical)
                    category_skills.append(canonical)
                    details.append({
                        'skill': canonical,
                        'category': category,
                        'matched_as': alias,
                    })

        if category_skills:
            categorized[category] = category_skills

    return {
        'skills': found_skills,
        'categorized': categorized,
        'details': details,
    }


def _match_skill(skill_name: str, text: str, text_lower: str) -> bool:
    """Check if a skill appears in text using word-boundary matching.

    Handles special characters in skill names (e.g., C++, C#, Node.js).

    Args:
        skill_name: The skill name to search for.
        text: Original text.
        text_lower: Lowercased text.

    Returns:
        True if the skill is found with proper word boundaries.
    """
    # Escape the skill name for regex, but handle special cases
    escaped = re.escape(skill_name)

    # Build pattern with word boundaries
    # For skills starting/ending with special chars (C++, C#), use custom boundaries
    if skill_name.endswith('+') or skill_name.endswith('#'):
        pattern = r'(?:^|\s|,|;|\(|\/)' + escaped + r'(?:$|\s|,|;|\)|\/)'
    elif '.' in skill_name:  # e.g., Node.js, Vue.js
        pattern = r'(?:^|\s|,|;|\()' + escaped + r'(?:$|\s|,|;|\))'
    else:
        pattern = r'\b' + escaped + r'\b'

    try:
        return bool(re.search(pattern, text, re.IGNORECASE))
    except re.error:
        # Fallback to simple containment for problematic patterns
        return skill_name.lower() in text_lower


def compare_skills(resume_skills: dict, job_skills: dict) -> dict:
    """Compare skills found in resume against job description.

    Args:
        resume_skills: Output from extract_skills for the resume.
        job_skills: Output from extract_skills for the job description.

    Returns:
        dict with keys:
            - 'matched': Skills present in both resume and JD.
            - 'missing': Skills in JD but not in resume.
            - 'additional': Skills in resume but not in JD.
            - 'matched_details': List of matched skill details with categories.
            - 'missing_details': List of missing skill details with categories.
            - 'additional_details': List of additional skill details with categories.
            - 'coverage': Skill coverage ratio (0.0 to 1.0).
            - 'coverage_percentage': Coverage as percentage string.
    """
    resume_set = resume_skills.get('skills', set())
    job_set = job_skills.get('skills', set())

    matched = resume_set & job_set
    missing = job_set - resume_set
    additional = resume_set - job_set

    # Build details with categories
    job_details_map = {d['skill']: d for d in job_skills.get('details', [])}
    resume_details_map = {d['skill']: d for d in resume_skills.get('details', [])}

    matched_details = []
    for skill in sorted(matched):
        detail = job_details_map.get(skill, resume_details_map.get(skill, {}))
        matched_details.append({
            'skill': skill,
            'category': detail.get('category', 'Other'),
        })

    missing_details = []
    for skill in sorted(missing):
        detail = job_details_map.get(skill, {})
        missing_details.append({
            'skill': skill,
            'category': detail.get('category', 'Other'),
        })

    additional_details = []
    for skill in sorted(additional):
        detail = resume_details_map.get(skill, {})
        additional_details.append({
            'skill': skill,
            'category': detail.get('category', 'Other'),
        })

    # Calculate coverage
    if len(job_set) > 0:
        coverage = len(matched) / len(job_set)
    else:
        coverage = 0.0

    return {
        'matched': matched,
        'missing': missing,
        'additional': additional,
        'matched_details': matched_details,
        'missing_details': missing_details,
        'additional_details': additional_details,
        'coverage': coverage,
        'coverage_percentage': f"{coverage * 100:.0f}%",
    }
