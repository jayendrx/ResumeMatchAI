"""Gap analysis module for identifying resume strengths and weaknesses."""


def analyze_gaps(resume_text: str, job_description: str,
                 skill_comparison: dict, semantic_score: dict) -> dict:
    """Analyze gaps between resume and job description.

    Args:
        resume_text: The resume text.
        job_description: The job description text.
        skill_comparison: Output from compare_skills.
        semantic_score: Output from calculate_semantic_similarity.

    Returns:
        dict with keys:
            - 'strengths': List of identified strengths.
            - 'weaknesses': List of identified weaknesses.
            - 'summary': Overall summary string.
    """
    strengths = []
    weaknesses = []

    matched = skill_comparison.get('matched', set())
    missing = skill_comparison.get('missing', set())
    additional = skill_comparison.get('additional', set())
    coverage = skill_comparison.get('coverage', 0.0)
    sim_pct = semantic_score.get('percentage', 0.0)

    resume_lower = resume_text.lower()
    jd_lower = job_description.lower()

    # --- Strengths ---

    # Strong skill coverage
    if coverage >= 0.7:
        strengths.append({
            'title': 'Strong Skill Coverage',
            'detail': (f'Your resume matches {len(matched)} out of '
                       f'{len(matched) + len(missing)} required skills '
                       f'({coverage * 100:.0f}% coverage). '
                       'This indicates strong technical alignment.'),
        })
    elif coverage >= 0.4:
        strengths.append({
            'title': 'Moderate Skill Coverage',
            'detail': (f'Your resume matches {len(matched)} out of '
                       f'{len(matched) + len(missing)} required skills. '
                       'You have a solid foundation for this role.'),
        })

    # Good semantic alignment
    if sim_pct >= 60:
        strengths.append({
            'title': 'Good Semantic Alignment',
            'detail': (f'Your resume achieves {sim_pct:.0f}% semantic similarity '
                       'with the job description, suggesting your experience '
                       'and language are well-aligned with the role.'),
        })

    # Specific matched skills
    if matched:
        matched_by_cat = {}
        for d in skill_comparison.get('matched_details', []):
            cat = d.get('category', 'Other')
            matched_by_cat.setdefault(cat, []).append(d['skill'])

        for cat, skills in matched_by_cat.items():
            if len(skills) >= 2:
                strengths.append({
                    'title': f'Strong {cat} Skills',
                    'detail': (f'You demonstrate proficiency in '
                               f'{", ".join(skills[:5])}'
                               f'{" and more" if len(skills) > 5 else ""}, '
                               f'which aligns well with the {cat.lower()} '
                               f'requirements of this role.'),
                })

    # Quantifiable achievements
    has_numbers = _has_quantifiable_achievements(resume_lower)
    if has_numbers:
        strengths.append({
            'title': 'Quantifiable Achievements',
            'detail': ('Your resume includes measurable achievements with '
                       'numbers and metrics, which strengthens the impact '
                       'of your experience descriptions.'),
        })

    # Additional valuable skills
    if len(additional) >= 3:
        strengths.append({
            'title': 'Diverse Skill Portfolio',
            'detail': (f'You possess {len(additional)} additional skills '
                       'beyond what the job description requires, '
                       'demonstrating breadth of expertise.'),
        })

    # Experience indicators
    experience_keywords = ['years of experience', 'year experience',
                          'led', 'managed', 'architected', 'designed',
                          'implemented', 'delivered', 'built', 'developed']
    exp_found = [kw for kw in experience_keywords if kw in resume_lower]
    if len(exp_found) >= 3:
        strengths.append({
            'title': 'Action-Oriented Language',
            'detail': ('Your resume uses strong action verbs and '
                       'experience-oriented language, which effectively '
                       'communicates your contributions.'),
        })

    # --- Weaknesses ---

    # Low skill coverage
    if coverage < 0.4 and len(missing) > 0:
        weaknesses.append({
            'title': 'Low Skill Coverage',
            'detail': (f'Your resume matches only {coverage * 100:.0f}% of '
                       f'the required skills. {len(missing)} skills mentioned '
                       'in the job description are not found in your resume.'),
        })

    # Low semantic alignment
    if sim_pct < 45:
        weaknesses.append({
            'title': 'Low Semantic Alignment',
            'detail': (f'The semantic similarity score is {sim_pct:.0f}%, '
                       'suggesting your resume uses quite different language '
                       'from the job description. Consider tailoring your '
                       'resume to better reflect the role\'s terminology.'),
        })

    # Missing skills by category
    if missing:
        missing_by_cat = {}
        for d in skill_comparison.get('missing_details', []):
            cat = d.get('category', 'Other')
            missing_by_cat.setdefault(cat, []).append(d['skill'])

        for cat, skills in missing_by_cat.items():
            if len(skills) >= 2:
                weaknesses.append({
                    'title': f'Missing {cat} Skills',
                    'detail': (f'The job description requires '
                               f'{", ".join(skills[:5])}'
                               f'{" and more" if len(skills) > 5 else ""} '
                               f'in {cat}, which are not evident in your resume.'),
                })

    # No quantifiable achievements
    if not has_numbers:
        weaknesses.append({
            'title': 'Lack of Quantifiable Achievements',
            'detail': ('Your resume may benefit from including more '
                       'measurable results, metrics, and quantifiable '
                       'achievements to demonstrate impact.'),
        })

    # Check for key JD terms not in resume
    jd_important_terms = _extract_important_terms(jd_lower)
    resume_important_terms = _extract_important_terms(resume_lower)
    missing_terms = jd_important_terms - resume_important_terms
    if len(missing_terms) >= 5:
        sample = list(missing_terms)[:5]
        weaknesses.append({
            'title': 'Missing Key Terminology',
            'detail': (f'Several terms from the job description are absent '
                       f'from your resume, including: {", ".join(sample)}. '
                       'Where applicable, consider incorporating relevant '
                       'terminology.'),
        })

    # Ensure we always have at least one item
    if not strengths:
        strengths.append({
            'title': 'Resume Submitted',
            'detail': ('You have a resume prepared for this application. '
                       'Focus on tailoring it to better match the job '
                       'description for improved results.'),
        })

    if not weaknesses:
        weaknesses.append({
            'title': 'Good Overall Alignment',
            'detail': ('No major gaps identified. Continue to keep your '
                       'resume updated with relevant experience and skills.'),
        })

    # Summary
    summary = _generate_summary(coverage, sim_pct, len(matched), len(missing))

    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'summary': summary,
    }


def _has_quantifiable_achievements(text: str) -> bool:
    """Check if the text contains quantifiable achievements."""
    import re
    patterns = [
        r'\d+%',           # percentages
        r'\$[\d,]+',       # dollar amounts
        r'\d+\+?\s*(users|customers|clients|projects|teams|members)',
        r'(increased|decreased|improved|reduced|grew|saved)\s+.*\d',
        r'\d+\s*(years?|months?)\s*(of)?\s*(experience)?',
    ]
    matches = sum(1 for p in patterns if re.search(p, text))
    return matches >= 2


def _extract_important_terms(text: str) -> set:
    """Extract important multi-word and single-word terms."""
    import re
    # Extract meaningful words (3+ chars, not common stopwords)
    stopwords = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
        'had', 'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been',
        'will', 'with', 'this', 'that', 'from', 'they', 'were', 'been',
        'would', 'there', 'their', 'what', 'about', 'which', 'when',
        'make', 'like', 'time', 'just', 'know', 'take', 'people',
        'into', 'year', 'your', 'some', 'them', 'than', 'then',
        'look', 'only', 'come', 'its', 'over', 'also', 'after',
        'should', 'must', 'able', 'such', 'work', 'working',
        'experience', 'including', 'strong', 'ability', 'using',
        'required', 'preferred', 'knowledge', 'understanding',
        'skills', 'skill', 'team', 'role', 'position', 'etc',
    }
    words = re.findall(r'\b[a-z]{3,}\b', text)
    return {w for w in words if w not in stopwords}


def _generate_summary(coverage: float, sim_pct: float,
                      matched_count: int, missing_count: int) -> str:
    """Generate an overall summary."""
    if coverage >= 0.7 and sim_pct >= 60:
        return (
            f'Your resume shows strong alignment with this role. '
            f'You match {matched_count} required skills with '
            f'{sim_pct:.0f}% semantic similarity. '
            f'Focus on highlighting your most relevant experience.'
        )
    elif coverage >= 0.4 or sim_pct >= 45:
        return (
            f'Your resume shows moderate alignment with this role. '
            f'You match {matched_count} required skills, but '
            f'{missing_count} are missing. Consider tailoring your '
            f'resume to address these gaps where applicable.'
        )
    else:
        return (
            f'Your resume has limited alignment with this specific role. '
            f'Only {matched_count} required skills are matched, and '
            f'semantic similarity is {sim_pct:.0f}%. Significant '
            f'tailoring may be needed for this position.'
        )
