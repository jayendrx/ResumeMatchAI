"""Semantic matching module using Sentence Transformers."""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Module-level model cache
_model = None


def get_model() -> SentenceTransformer:
    """Load and cache the sentence transformer model.

    Returns:
        SentenceTransformer model instance.
    """
    global _model
    if _model is None:
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model


def calculate_semantic_similarity(resume_text: str, job_description: str) -> dict:
    """Calculate semantic similarity between resume and job description.

    Uses sentence-transformers/all-MiniLM-L6-v2 to encode both texts
    and computes cosine similarity.

    Args:
        resume_text: The resume text.
        job_description: The job description text.

    Returns:
        dict with keys:
            - 'raw_score': Raw cosine similarity (-1 to 1).
            - 'percentage': Score as a percentage (0 to 100).
            - 'interpretation': Human-readable interpretation.
    """
    if not resume_text or not job_description:
        return {
            'raw_score': 0.0,
            'percentage': 0.0,
            'interpretation': 'Insufficient text for analysis.',
        }

    model = get_model()

    # Encode texts
    resume_embedding = model.encode([resume_text])
    job_embedding = model.encode([job_description])

    # Calculate cosine similarity
    similarity = cosine_similarity(resume_embedding, job_embedding)[0][0]

    # Convert to percentage (cosine similarity ranges from -1 to 1,
    # but for text it's typically 0 to 1)
    percentage = float(max(0, min(100, similarity * 100)))

    # Provide interpretation
    interpretation = _interpret_score(percentage)

    return {
        'raw_score': float(similarity),
        'percentage': round(percentage, 1),
        'interpretation': interpretation,
    }


def calculate_section_similarities(resume_text: str, job_description: str,
                                    chunk_size: int = 3) -> list:
    """Calculate similarity for chunks of the resume against the job description.

    Splits the resume into sentence chunks and calculates similarity of
    each chunk against the full job description.

    Args:
        resume_text: The resume text.
        job_description: The job description text.
        chunk_size: Number of sentences per chunk.

    Returns:
        List of dicts with 'text' and 'similarity' for each chunk.
    """
    if not resume_text or not job_description:
        return []

    model = get_model()

    # Simple sentence splitting
    sentences = [s.strip() for s in resume_text.replace('\n', '. ').split('.')
                 if s.strip() and len(s.strip()) > 10]

    if not sentences:
        return []

    # Create chunks
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunk = '. '.join(sentences[i:i + chunk_size])
        chunks.append(chunk)

    if not chunks:
        return []

    # Encode all chunks and job description
    chunk_embeddings = model.encode(chunks)
    job_embedding = model.encode([job_description])

    # Calculate similarity for each chunk
    results = []
    for i, chunk in enumerate(chunks):
        sim = cosine_similarity([chunk_embeddings[i]], job_embedding)[0][0]
        results.append({
            'text': chunk[:200] + '...' if len(chunk) > 200 else chunk,
            'similarity': float(max(0, sim)),
        })

    # Sort by similarity descending
    results.sort(key=lambda x: x['similarity'], reverse=True)

    return results


def _interpret_score(percentage: float) -> str:
    """Provide a human-readable interpretation of the similarity score."""
    if percentage >= 75:
        return (
            'Strong alignment - Your resume shows strong semantic similarity '
            'with the job description. The language and themes are well-matched.'
        )
    elif percentage >= 55:
        return (
            'Moderate alignment - Your resume shares relevant themes with the '
            'job description, but there is room to better align your language '
            'and emphasis with the role requirements.'
        )
    elif percentage >= 35:
        return (
            'Partial alignment - Some overlap exists, but your resume could '
            'benefit from incorporating more language and themes from the '
            'job description where they truthfully apply.'
        )
    else:
        return (
            'Low alignment - Your resume and the job description use quite '
            'different language. Consider tailoring your resume to reflect '
            'the terminology and focus areas of the target role, where applicable.'
        )
