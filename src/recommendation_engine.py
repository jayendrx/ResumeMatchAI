"""Recommendation engine for generating actionable resume improvement suggestions."""


def generate_recommendations(resume_text: str, job_description: str,
                             skill_comparison: dict, semantic_score: dict,
                             gap_analysis: dict) -> list:
    """Generate actionable recommendations based on the analysis.

    Does NOT fabricate achievements, qualifications, or skills.
    Suggestions focus on improving visibility, relevance, and presentation
    of genuine experience.

    Args:
        resume_text: The resume text.
        job_description: The job description text.
        skill_comparison: Output from compare_skills.
        semantic_score: Output from calculate_semantic_similarity.
        gap_analysis: Output from analyze_gaps.

    Returns:
        List of recommendation dicts with 'title', 'explanation', 'action'.
    """
    recommendations = []
    missing = skill_comparison.get('missing', set())
    matched = skill_comparison.get('matched', set())
    coverage = skill_comparison.get('coverage', 0.0)
    sim_pct = semantic_score.get('percentage', 0.0)
    resume_lower = resume_text.lower()

    # 1. Address missing skills
    if missing:
        missing_list = sorted(missing)
        top_missing = missing_list[:5]
        recommendations.append({
            'title': 'Address Missing Skills',
            'explanation': (
                f'The job description mentions {len(missing)} skills not '
                f'found in your resume: {", ".join(top_missing)}'
                f'{" and more" if len(missing) > 5 else ""}.'
            ),
            'action': (
                'If you have experience with any of these skills, '
                'make sure they are explicitly mentioned in your resume. '
                'Add them to your skills section and reference them in '
                'relevant project or experience descriptions. Only add '
                'skills you genuinely possess.'
            ),
        })

    # 2. Improve semantic alignment
    if sim_pct < 60:
        recommendations.append({
            'title': 'Improve Semantic Alignment',
            'explanation': (
                f"Your resume's semantic similarity score is {sim_pct:.0f}%, "
                'indicating that the language and themes in your resume '
                'differ from the job description.'
            ),
            'action': (
                "Review the job description's key phrases and terminology. "
                'Where applicable, incorporate similar language into your '
                'professional summary and experience descriptions. '
                "Mirror the job's tone and focus areas where your "
                'experience genuinely applies.'
            ),
        })

    # 3. Add quantifiable achievements
    import re
    has_metrics = bool(re.search(r'\d+%|\$[\d,]+', resume_lower))
    if not has_metrics:
        recommendations.append({
            'title': 'Add Quantifiable Achievements',
            'explanation': (
                'Your resume does not appear to include measurable '
                'results or quantified achievements.'
            ),
            'action': (
                'Where possible, quantify your achievements. For example: '
                '"Improved system performance by 40%" or '
                '"Managed a team of 8 engineers" or '
                '"Reduced deployment time from 2 hours to 15 minutes". '
                'Numbers make your contributions tangible and memorable.'
            ),
        })

    # 4. Tailor professional summary
    has_summary = any(kw in resume_lower for kw in
                      ['summary', 'objective', 'profile', 'about me'])
    if not has_summary:
        recommendations.append({
            'title': 'Add a Professional Summary',
            'explanation': (
                'Your resume does not appear to have a prominent '
                'professional summary or profile section.'
            ),
            'action': (
                'Add a 2-3 sentence professional summary at the top of '
                'your resume that highlights your most relevant '
                'experience and skills for this specific role. '
                'This immediately communicates your fit to the reader.'
            ),
        })
    elif sim_pct < 55:
        recommendations.append({
            'title': 'Tailor Your Professional Summary',
            'explanation': (
                'Your resume has a summary section, but it may not be '
                'well-aligned with this specific job description.'
            ),
            'action': (
                'Rewrite your professional summary to directly address '
                'the key requirements of this role. Highlight the '
                'experience and skills that are most relevant to '
                'the job description.'
            ),
        })

    # 5. Highlight relevant projects
    has_projects = 'project' in resume_lower
    if not has_projects and len(matched) > 0:
        recommendations.append({
            'title': 'Add Relevant Projects',
            'explanation': (
                'Your resume does not appear to showcase specific projects. '
                'Projects provide concrete evidence of your skills.'
            ),
            'action': (
                'Add a Projects section that highlights 2-3 relevant '
                'projects demonstrating your expertise with the matched '
                'skills. Describe the problem, your approach, '
                'technologies used, and the outcome.'
            ),
        })

    # 6. Use action verbs
    action_verbs = ['developed', 'implemented', 'designed', 'led',
                    'built', 'created', 'managed', 'optimized',
                    'architected', 'delivered', 'deployed', 'automated']
    found_verbs = [v for v in action_verbs if v in resume_lower]
    if len(found_verbs) < 3:
        recommendations.append({
            'title': 'Strengthen Action Language',
            'explanation': (
                'Your resume could benefit from stronger action verbs '
                'to describe your accomplishments.'
            ),
            'action': (
                'Begin each experience bullet point with a strong '
                'action verb such as "Developed", "Implemented", '
                '"Designed", "Led", "Optimized", or "Delivered". '
                'This creates more impactful descriptions of your work.'
            ),
        })

    # 7. Missing skill categories
    missing_details = skill_comparison.get('missing_details', [])
    missing_cats = set(d['category'] for d in missing_details)
    for cat in sorted(missing_cats):
        cat_skills = [d['skill'] for d in missing_details
                      if d['category'] == cat]
        if len(cat_skills) >= 2:
            recommendations.append({
                'title': f'Build {cat} Expertise',
                'explanation': (
                    f'The job requires {cat.lower()} skills: '
                    f'{", ".join(cat_skills[:4])}. '
                    'These are not currently visible in your resume.'
                ),
                'action': (
                    f'If you have experience in these areas, add them to '
                    f'your resume. If not, consider building expertise '
                    f'through courses, certifications, or side projects '
                    f'in {cat.lower()}.'
                ),
            })

    # 8. Keyword optimization
    if coverage < 0.5 and len(missing) > 3:
        recommendations.append({
            'title': 'Optimize Keywords',
            'explanation': (
                'Many key terms from the job description are missing '
                'from your resume. ATS systems often scan for specific keywords.'
            ),
            'action': (
                'Review the job description and identify the most '
                'important technical terms and phrases. Ensure these '
                'keywords appear naturally in your resume where they '
                'accurately describe your experience. Avoid keyword '
                'stuffing with skills you do not possess.'
            ),
        })

    # Ensure at least 3 recommendations
    if len(recommendations) < 3:
        defaults = [
            {
                'title': 'Keep Your Resume Concise',
                'explanation': 'Concise resumes are more effective.',
                'action': (
                    'Aim for a 1-2 page resume. Remove outdated or '
                    'irrelevant experience. Focus on the most recent '
                    'and relevant roles that align with this position.'
                ),
            },
            {
                'title': 'Proofread and Format Consistently',
                'explanation': 'Professional presentation matters.',
                'action': (
                    'Ensure consistent formatting, proper spelling, '
                    'and grammatical accuracy throughout your resume. '
                    'Use a clean, professional template.'
                ),
            },
            {
                'title': 'Include Relevant Certifications',
                'explanation': 'Certifications validate your expertise.',
                'action': (
                    'If you hold any certifications relevant to this role, '
                    'ensure they are prominently listed. Consider obtaining '
                    'certifications that align with the job requirements.'
                ),
            },
        ]
        for rec in defaults:
            if len(recommendations) >= 3:
                break
            if not any(r['title'] == rec['title'] for r in recommendations):
                recommendations.append(rec)

    return recommendations


def generate_roast(resume_text: str, job_description: str,
                   skill_comparison: dict, semantic_score: dict) -> list:
    """Generate witty, constructive roast-style feedback.

    Provides honest, humorous but respectful critique of the resume.

    Args:
        resume_text: The resume text.
        job_description: The job description text.
        skill_comparison: Output from compare_skills.
        semantic_score: Output from calculate_semantic_similarity.

    Returns:
        List of roast strings.
    """
    roasts = []
    missing = skill_comparison.get('missing', set())
    matched = skill_comparison.get('matched', set())
    additional = skill_comparison.get('additional', set())
    coverage = skill_comparison.get('coverage', 0.0)
    sim_pct = semantic_score.get('percentage', 0.0)
    resume_lower = resume_text.lower()

    # Score-based roasts
    if sim_pct < 30:
        roasts.append(
            "Your resume and this job description are so different, "
            "they might not even be from the same industry. "
            "Time for a major rewrite! 🔥"
        )
    elif sim_pct < 50:
        roasts.append(
            f"A {sim_pct:.0f}% semantic match? Your resume is giving "
            "'close but no cigar' energy. Let's bridge that gap! 🤔"
        )
    elif sim_pct >= 80:
        roasts.append(
            f"Wow, {sim_pct:.0f}% match! Either you're the perfect candidate "
            "or you copied the job description. Either way, impressive! 🎯"
        )

    # Skill-based roasts
    if len(missing) > len(matched) and len(missing) > 0:
        roasts.append(
            f"You're missing {len(missing)} skills that the job asks for "
            f"but only matching {len(matched)}. Your resume is playing "
            "hide and seek with the requirements. 🙈"
        )

    if coverage == 0 and len(missing) > 0:
        roasts.append(
            "Zero skill coverage? Bold strategy. You might want to at "
            "least pretend you read the job description. 😏"
        )
    elif coverage >= 0.9:
        roasts.append(
            f"With {coverage * 100:.0f}% skill coverage, you're basically "
            "overqualified. Make sure they're paying you enough! 💰"
        )

    # Content-based roasts
    if len(resume_lower) < 200:
        roasts.append(
            "Your resume is shorter than some tweets. Brevity is the soul "
            "of wit, but recruiters need something to work with. 📝"
        )
    elif len(resume_lower) > 5000:
        roasts.append(
            "Your resume is longer than some novels. Recruiters spend "
            "6 seconds on average — yours needs a table of contents. 📚"
        )

    # Buzzword check
    buzzwords = ['synergy', 'leverage', 'paradigm', 'holistic',
                 'disruptive', 'bleeding edge', 'rockstar', 'ninja',
                 'guru', '10x', 'thought leader']
    found_buzz = [b for b in buzzwords if b in resume_lower]
    if found_buzz:
        buzz_str = ", ".join(found_buzz)
        roasts.append(
            f"Buzzword alert! Found: {buzz_str}. "
            "The 2010s called — they want their corporate jargon back. 🤓"
        )

    # Missing metrics
    import re
    if not re.search(r'\d+%|\$[\d,]+', resume_lower):
        roasts.append(
            "Not a single percentage or dollar amount in sight. "
            "How do we know you actually accomplished anything? "
            "Add some numbers! 📊"
        )

    # Action verb check
    weak_verbs = ['responsible for', 'helped with', 'assisted in',
                  'worked on', 'involved in', 'participated in']
    found_weak = [v for v in weak_verbs if v in resume_lower]
    if found_weak:
        roasts.append(
            f"'{found_weak[0].title()}'? That's the resume equivalent of "
            '"I was in the room when things happened." Lead with impact! 💪'
        )

    # Additional skills nobody asked for
    if len(additional) > len(matched) + 3 and len(additional) > 5:
        roasts.append(
            f"You listed {len(additional)} skills the job doesn't even need. "
            "Quality over quantity! This isn't a Pokémon — you don't need "
            "to catch 'em all. 😎"
        )

    # Always end positively
    if matched:
        roasts.append(
            f"But hey, you do match {len(matched)} key skills. "
            "With some polishing, this resume could really shine. "
            "You've got potential! 🌟"
        )
    else:
        roasts.append(
            "Look, everyone starts somewhere. Take the recommendations above, "
            "give your resume some love, and try again. You've got this! 💪"
        )

    return roasts
