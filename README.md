# Resume Match AI — Intelligent Resume & Job Description Analyzer

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-purple.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF%20Export-green.svg)](https://www.reportlab.com/)

**Resume Match AI** (also featuring **Resume Roast AI**) is a production-quality, academic Natural Language Processing (NLP) application that intelligently evaluates a candidate's resume against an target job description. It performs semantic text alignment, multi-category skill taxonomy matching, gap analysis, actionable recommendation generation, witty constructive critiques, and downloadable PDF report generation.

The application operates completely locally without paid APIs, external cloud inference, or OpenAI dependencies.

---

## 🎯 Key Capabilities & Features

1. **Text Extraction & Cleaning**:
   - Parses text from PDF resumes with paragraph and layout preservation via `pypdf`.
   - Handles multi-page PDFs, encrypted files, and flags image-only/scanned documents gracefully.
   - Cleans formatting artifacts, unicode symbols, URLs, emails, and contact details while strictly preserving technical vocabulary, programming symbols (`C++`, `C#`, `.NET`), and numerical metrics.

2. **Genuine Semantic Similarity Pipeline**:
   - Uses the pretrained `sentence-transformers/all-MiniLM-L6-v2` transformer model.
   - Computes dense text embeddings and Scikit-Learn cosine similarity.
   - Clearly presents the result as a **Semantic Match Score** (textual alignment), with full academic transparency explaining that it measures linguistic and thematic alignment rather than an arbitrary hiring probability.

3. **Taxonomy-Driven Skill Extraction**:
   - Word-boundary-aware, case-insensitive regex parsing across 10 distinct technical domains (Programming, Machine Learning, Data, Cloud & DevOps, Databases, Web Development, Soft Skills, Security, Mobile, Testing).
   - Resolves aliases (e.g., `ML` $\rightarrow$ `Machine Learning`, `K8s` $\rightarrow$ `Kubernetes`, `JS` $\rightarrow$ `JavaScript`).
   - Prevents substring false positives (e.g., `Go` vs `Good`, `Java` vs `JavaScript`).

4. **Skill Matching & Gap Analysis**:
   - Categorizes skills into **Matched**, **Missing**, and **Additional**.
   - Calculates a separate **Skill Coverage Score** ($M_{matched} / N_{required}$).
   - Identifies candidate strengths and areas for improvement based on quantifiable achievements, action verbs, and domain competency.

5. **Actionable Recommendation Engine**:
   - Generates grounded, concrete suggestions (e.g., highlighting missing competencies, tailoring summary sections, adding quantifiable metrics).
   - Never fabricates fake credentials or advises manipulating ATS systems dishonestly.

6. **"Roast My Resume"**:
   - Delivers an honest, constructive, and witty critique of the resume's alignment, buzzwords, conciseness, and metrics.

7. **Exportable PDF Analysis Report**:
   - Generates a styled, publication-ready PDF summary report with ReportLab.

8. **Demo Mode**:
   - Includes built-in one-click demonstration data for quick classroom presentations or academic evaluation.

---

## 📂 Project Architecture

```
ResumeMatchAI/
│
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation & academic report
├── .gitignore                  # Git ignore rules
│
├── src/                        # Core NLP & processing modules
│   ├── __init__.py
│   ├── resume_parser.py        # PDF text extraction & validation
│   ├── text_preprocessor.py    # Text cleaning & section parsing
│   ├── semantic_matcher.py     # Sentence Transformers & cosine similarity
│   ├── skill_extractor.py      # Taxonomy lookup & regex boundary extraction
│   ├── gap_analyzer.py         # Strengths & weaknesses identification
│   ├── recommendation_engine.py# Actionable guidance & resume roast
│   └── report_generator.py     # ReportLab PDF report generation
│
├── data/
│   └── skills_taxonomy.json    # Configurable taxonomy of skills and aliases
│
├── assets/
│   └── style.css               # Dark navy UI theme with violet/blue accents
│
└── tests/                      # Automated unit test suite
    ├── test_parser.py          # PDF parser tests
    ├── test_matcher.py         # Text preprocessor & matcher tests
    └── test_skill_extractor.py # Skill taxonomy & extraction tests
```

---

## 🛠️ Technology Stack

| Component | Library / Model | Purpose |
| :--- | :--- | :--- |
| **User Interface** | `Streamlit 1.28+`, HTML5/CSS3 | Interactive responsive dashboard |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Dense sentence representations (384-d) |
| **Similarity** | `scikit-learn` | Cosine similarity calculation |
| **Skill Extraction** | Regular expressions with JSON taxonomy | Boundary-safe entity recognition |
| **PDF Extraction** | `pypdf` | Multi-page PDF text extraction |
| **Visualizations** | `Plotly` | Gauge charts and skill breakdown bars |
| **PDF Generation** | `ReportLab` | Downloadable evaluation reports |

---

## 🚀 Installation & Running Locally

### 1. Prerequisites
- Python 3.11 or Python 3.12 installed on your machine.
- Git (optional).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Running the Test Suite
```bash
python -m unittest discover tests
```

---

## 🔬 NLP Methodology & Equations

### 1. Semantic Similarity
Let $\mathbf{u} = \text{Encoder}(\text{Resume})$ and $\mathbf{v} = \text{Encoder}(\text{Job Description})$ be the 384-dimensional dense vectors produced by `all-MiniLM-L6-v2`. The semantic match is given by cosine similarity:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$

The score is normalized to a percentage $[0, 100]\%$.

### 2. Skill Coverage Ratio
Let $S_{JD}$ be the set of canonical skills extracted from the job description and $S_{Resume}$ be the set of canonical skills extracted from the resume:

$$\text{Coverage} = \frac{|S_{Resume} \cap S_{JD}|}{|S_{JD}|} \quad (\text{for } |S_{JD}| > 0)$$

---

## 📄 License
Academic & Educational Use Only. Built for NLP coursework and research demonstrations.
