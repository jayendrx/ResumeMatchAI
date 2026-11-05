"""Resume Roast AI — Intelligent Resume & Job Description Analyzer.

A Streamlit application that uses NLP to compare resumes against job
descriptions and provide actionable feedback.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------------------------
# Page configuration (MUST be the first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Resume Roast AI",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Load custom CSS
# ---------------------------------------------------------------------------
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Module imports (after page config)
# ---------------------------------------------------------------------------
from src.resume_parser import extract_resume_text
from src.text_preprocessor import preprocess_text
from src.semantic_matcher import calculate_semantic_similarity, get_model
from src.skill_extractor import extract_skills, compare_skills, load_taxonomy
from src.gap_analyzer import analyze_gaps
from src.recommendation_engine import generate_recommendations, generate_roast
from src.report_generator import generate_report


# ---------------------------------------------------------------------------
# Cache the sentence-transformer model
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_nlp_model():
    """Load and cache the sentence transformer model."""
    return get_model()


@st.cache_data(show_spinner=False)
def load_skills_taxonomy():
    """Load and cache the skills taxonomy."""
    return load_taxonomy()


# ---------------------------------------------------------------------------
# Demo data
# ---------------------------------------------------------------------------
DEMO_RESUME = """SARAH CHEN
Senior Machine Learning Engineer
San Francisco, CA | sarah.chen@email.com | linkedin.com/in/sarahchen

PROFESSIONAL SUMMARY
Results-driven Machine Learning Engineer with 5+ years of experience designing
and deploying production ML systems. Expert in Python, TensorFlow, PyTorch, and
cloud infrastructure. Passionate about NLP and computer vision applications.
Led teams of 4-8 engineers to deliver scalable ML solutions processing millions
of records daily. Published researcher with 3 papers in top-tier conferences.

EXPERIENCE

Senior ML Engineer | TechCorp AI Division | 2021 - Present
- Designed and deployed a real-time NLP pipeline processing 2M+ documents daily
  using BERT and custom transformer architectures on AWS
- Improved model inference latency by 65% through model optimization and
  TensorRT integration, reducing costs by $180K annually
- Led a team of 6 engineers to build a recommendation system increasing user
  engagement by 23%
- Implemented CI/CD pipelines for ML model deployment using Docker, Kubernetes,
  and GitHub Actions
- Developed A/B testing framework for model evaluation across 15+ experiments

ML Engineer | DataDriven Inc. | 2019 - 2021
- Built computer vision models for defect detection achieving 94% accuracy,
  reducing manual inspection time by 40%
- Developed data pipelines using Apache Spark and Airflow processing 500GB+
  daily
- Created interactive dashboards using Plotly and Streamlit for model monitoring
- Implemented feature engineering pipelines using Pandas, NumPy, and Scikit-learn

Junior Data Scientist | Analytics Pro | 2018 - 2019
- Performed statistical analysis and hypothesis testing on customer datasets
- Built predictive models using Random Forest and XGBoost with 87% accuracy
- Automated reporting workflows using Python, saving 15 hours per week
- Collaborated with cross-functional teams to translate business requirements
  into technical solutions

EDUCATION
M.S. Computer Science (Machine Learning) | Stanford University | 2018
B.S. Mathematics | UC Berkeley | 2016

SKILLS
Python, TensorFlow, PyTorch, Scikit-learn, SQL, Java, C++
Machine Learning, Deep Learning, NLP, Computer Vision, Transformers
Pandas, NumPy, Apache Spark, Airflow, Data Visualization
AWS, Docker, Kubernetes, Git, CI/CD, GitHub Actions
Communication, Leadership, Teamwork, Problem Solving, Agile

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Google Professional Machine Learning Engineer

PUBLICATIONS
- "Efficient Transformer Architectures for Document Classification" - ACL 2022
- "Scalable Computer Vision Pipeline for Industrial Inspection" - CVPR 2021
"""

DEMO_JOB = """Senior Machine Learning Engineer

About the Role:
We are seeking a Senior Machine Learning Engineer to join our AI team. You will
design, build, and deploy ML models that power our core products serving
millions of users. You'll work closely with product, engineering, and research
teams to push the boundaries of applied AI.

Responsibilities:
- Design and implement production ML systems for NLP and recommendation tasks
- Build and optimize deep learning models using PyTorch and TensorFlow
- Develop scalable data pipelines for model training and inference
- Lead ML experiments and A/B tests to improve model performance
- Mentor junior engineers and contribute to technical architecture decisions
- Deploy models to cloud infrastructure using Docker and Kubernetes
- Implement monitoring and alerting for model performance in production

Requirements:
- 4+ years of experience in machine learning engineering
- Strong proficiency in Python, SQL, and ML frameworks (PyTorch, TensorFlow)
- Experience with NLP, recommendation systems, or computer vision
- Hands-on experience with cloud platforms (AWS, GCP, or Azure)
- Experience with Docker, Kubernetes, and CI/CD pipelines
- Strong understanding of statistics and experimental design
- Experience with data processing frameworks (Spark, Pandas, Airflow)
- Excellent communication and collaboration skills
- M.S. or Ph.D. in Computer Science, Machine Learning, or related field

Nice to Have:
- Published research in ML/AI conferences
- Experience with Large Language Models and Generative AI
- Knowledge of MLOps best practices
- Experience with Scikit-learn, XGBoost, or similar libraries
- Familiarity with Streamlit, Plotly, or similar visualization tools
- Experience leading technical teams

Skills:
Python, PyTorch, TensorFlow, SQL, Machine Learning, Deep Learning,
NLP, Computer Vision, AWS, Docker, Kubernetes, CI/CD, Git,
Pandas, Apache Spark, Airflow, Scikit-learn, Statistics,
Communication, Leadership, Teamwork, Agile, Problem Solving
"""


# ---------------------------------------------------------------------------
# Analysis pipeline
# ---------------------------------------------------------------------------
def run_analysis(resume_text: str, job_description: str) -> dict:
    """Run the complete NLP analysis pipeline.

    Args:
        resume_text: Preprocessed resume text.
        job_description: Job description text.

    Returns:
        Dictionary with all analysis results.
    """
    # Load resources
    taxonomy = load_skills_taxonomy()

    # Step 1: Preprocess
    clean_resume = preprocess_text(resume_text)
    clean_jd = preprocess_text(job_description)

    # Step 2: Semantic similarity
    semantic_score = calculate_semantic_similarity(clean_resume, clean_jd)

    # Step 3: Skill extraction
    resume_skills = extract_skills(resume_text, taxonomy)
    job_skills = extract_skills(job_description, taxonomy)

    # Step 4: Skill comparison
    skill_comparison = compare_skills(resume_skills, job_skills)

    # Step 5: Gap analysis
    gap_analysis = analyze_gaps(
        resume_text, job_description, skill_comparison, semantic_score
    )

    # Step 6: Recommendations
    recommendations = generate_recommendations(
        resume_text, job_description, skill_comparison, semantic_score,
        gap_analysis
    )

    # Step 7: Roast
    roasts = generate_roast(
        resume_text, job_description, skill_comparison, semantic_score
    )

    return {
        'semantic_score': semantic_score,
        'resume_skills': resume_skills,
        'job_skills': job_skills,
        'skill_comparison': skill_comparison,
        'gap_analysis': gap_analysis,
        'recommendations': recommendations,
        'roasts': roasts,
    }


# ---------------------------------------------------------------------------
# UI helper functions
# ---------------------------------------------------------------------------
def render_metric_card(label: str, value: str, sublabel: str = ""):
    """Render a styled metric card."""
    sublabel_html = (
        f'<div class="metric-sublabel">{sublabel}</div>' if sublabel else ""
    )
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sublabel_html}
    </div>
    """, unsafe_allow_html=True)


def render_skill_tags(skills_details: list, css_class: str):
    """Render skill tags with categories."""
    if not skills_details:
        st.markdown(
            '<p style="color: #7986cb; font-style: italic;">None found</p>',
            unsafe_allow_html=True,
        )
        return
    tags_html = ""
    for d in skills_details:
        tags_html += (
            f'<span class="skill-tag {css_class}">{d["skill"]}'
            f'<span class="category-badge"> · {d["category"]}</span></span>'
        )
    st.markdown(tags_html, unsafe_allow_html=True)


def render_skills_chart(skill_comparison: dict):
    """Render a bar chart of skills by category."""
    matched_details = skill_comparison.get('matched_details', [])
    missing_details = skill_comparison.get('missing_details', [])

    # Aggregate by category
    categories = {}
    for d in matched_details:
        cat = d['category']
        categories.setdefault(cat, {'matched': 0, 'missing': 0})
        categories[cat]['matched'] += 1
    for d in missing_details:
        cat = d['category']
        categories.setdefault(cat, {'matched': 0, 'missing': 0})
        categories[cat]['missing'] += 1

    if not categories:
        return

    cats = sorted(categories.keys())
    matched_vals = [categories[c]['matched'] for c in cats]
    missing_vals = [categories[c]['missing'] for c in cats]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Matched',
        x=cats, y=matched_vals,
        marker_color='#4caf50',
        marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        name='Missing',
        x=cats, y=missing_vals,
        marker_color='#ff9800',
        marker_line_width=0,
    ))

    fig.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9fa8da', size=12),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02,
            xanchor='right', x=1,
            font=dict(color='#b3b8e8'),
        ),
        margin=dict(l=40, r=20, t=40, b=60),
        height=350,
        xaxis=dict(
            gridcolor='#1a2040',
            tickangle=-30,
        ),
        yaxis=dict(
            gridcolor='#1a2040',
            title='Number of Skills',
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_similarity_gauge(percentage: float):
    """Render a gauge chart for semantic similarity."""
    if percentage >= 70:
        bar_color = "#4caf50"
    elif percentage >= 45:
        bar_color = "#ff9800"
    else:
        bar_color = "#f44336"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number={'suffix': '%', 'font': {'color': '#e8eaf6', 'size': 40}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickcolor': '#5c6bc0',
                'tickwidth': 1,
                'dtick': 20,
                'tickfont': {'color': '#7986cb', 'size': 10},
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': '#1a1f3a',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 35], 'color': 'rgba(244,67,54,0.08)'},
                {'range': [35, 55], 'color': 'rgba(255,152,0,0.08)'},
                {'range': [55, 75], 'color': 'rgba(76,175,80,0.06)'},
                {'range': [75, 100], 'color': 'rgba(76,175,80,0.12)'},
            ],
        },
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#9fa8da'),
        height=220,
        margin=dict(l=30, r=30, t=30, b=10),
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------
def main():
    # --- Header ---
    st.markdown(
        '<div class="header-badge">INTELLIGENT NLP ANALYSIS</div>',
        unsafe_allow_html=True,
    )
    st.markdown("# 🔥 Resume Roast AI")
    st.markdown(
        '<p class="header-subtitle">'
        "Your AI-powered career companion. Discover how well your resume "
        "aligns with your dream job."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # --- Initialize session state ---
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    if 'job_description' not in st.session_state:
        st.session_state.job_description = ""
    if 'demo_loaded' not in st.session_state:
        st.session_state.demo_loaded = False

    # --- Two-column layout ---
    left_col, right_col = st.columns([1, 2], gap="large")

    # ===================== LEFT COLUMN — INPUT PANEL =========================
    with left_col:
        st.markdown(
            '<div class="input-panel">',
            unsafe_allow_html=True,
        )
        st.markdown("### 📄 Upload Your Resume")

        uploaded_file = st.file_uploader(
            "Upload your resume (PDF)",
            type=["pdf"],
            help="Maximum file size: 10 MB. Only text-based PDFs are supported.",
        )

        resume_text = ""

        if uploaded_file is not None:
            if uploaded_file.size > 10 * 1024 * 1024:
                st.error("File size exceeds 10 MB. Please upload a smaller file.")
            else:
                with st.spinner("Extracting text from PDF..."):
                    result = extract_resume_text(uploaded_file)

                if result['success']:
                    resume_text = result['text']
                    st.success(
                        f"✅ Successfully extracted text from "
                        f"{result['page_count']} page(s)."
                    )
                    with st.expander("Preview extracted text", expanded=False):
                        st.text(resume_text[:2000] + (
                            "..." if len(resume_text) > 2000 else ""
                        ))
                else:
                    st.error(f"❌ {result['error']}")

        # Use demo text if loaded
        if st.session_state.demo_loaded and not resume_text:
            resume_text = st.session_state.resume_text

        st.markdown("---")
        st.markdown("### 💼 Job Description")

        jd_default = (
            st.session_state.job_description
            if st.session_state.demo_loaded
            else ""
        )
        job_description = st.text_area(
            "Paste the job description",
            value=jd_default,
            height=250,
            placeholder="Paste the full job description here...",
            help="Include the complete job listing for best results.",
        )

        # Character counter
        char_count = len(job_description)
        st.markdown(
            f'<div class="char-counter">{char_count:,} characters</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Validate inputs
        has_resume = bool(resume_text and len(resume_text.strip()) > 50)
        has_jd = bool(job_description and len(job_description.strip()) > 50)
        inputs_valid = has_resume and has_jd

        if not has_resume and uploaded_file is not None:
            st.info("📝 Resume text is too short. Please check the uploaded file.")
        if not has_jd and char_count > 0:
            st.info("📝 Job description needs at least 50 characters.")

        # Analyze button
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            analyze_clicked = st.button(
                "🔍 Analyze Resume",
                disabled=not inputs_valid,
                use_container_width=True,
            )
        with col_btn2:
            demo_clicked = st.button(
                "📋 Load Demo",
                use_container_width=True,
            )

        if demo_clicked:
            st.session_state.resume_text = DEMO_RESUME
            st.session_state.job_description = DEMO_JOB
            st.session_state.demo_loaded = True
            st.session_state.analysis_results = None
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ===================== RIGHT COLUMN — RESULTS PANEL ======================
    with right_col:
        if analyze_clicked and inputs_valid:
            with st.spinner("🔥 Analyzing your resume... This may take a moment."):
                # Ensure model is loaded
                load_nlp_model()
                results = run_analysis(resume_text, job_description)
                st.session_state.analysis_results = results

        results = st.session_state.analysis_results

        if results is None:
            # Empty state
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-text">Your resume analysis will appear here</div>
                <div class="empty-state-subtext">
                    Upload your resume and paste a job description to get started,
                    or click "Load Demo" to try it out.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            render_results(results)


def render_results(results: dict):
    """Render the complete results dashboard."""
    semantic = results['semantic_score']
    skill_comp = results['skill_comparison']
    gap = results['gap_analysis']
    recs = results['recommendations']
    roasts = results['roasts']

    # ── A. Overview KPI Cards ──
    st.markdown("### 📊 Analysis Overview")

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        render_metric_card(
            "Semantic Match",
            f"{semantic['percentage']:.0f}%",
            "Textual alignment score",
        )
    with kpi2:
        render_metric_card(
            "Skill Coverage",
            skill_comp['coverage_percentage'],
            f"{len(skill_comp['matched'])} of "
            f"{len(skill_comp['matched']) + len(skill_comp['missing'])} skills",
        )
    with kpi3:
        render_metric_card(
            "Matched Skills",
            str(len(skill_comp['matched'])),
            "Skills found in both",
        )

    st.markdown("")

    # Semantic similarity detail
    with st.expander("📐 Semantic Similarity Detail", expanded=False):
        sim_col1, sim_col2 = st.columns([1, 2])
        with sim_col1:
            render_similarity_gauge(semantic['percentage'])
        with sim_col2:
            st.markdown(f"**Interpretation:** {semantic['interpretation']}")
            st.caption(
                "ℹ️ Semantic similarity measures how closely the language "
                "and themes in your resume match the job description. "
                "It is NOT a prediction of hiring probability."
            )

    st.markdown("---")

    # ── B. Skills Analysis ──
    st.markdown("### 🎯 Skills Analysis")

    tab1, tab2, tab3 = st.tabs([
        f"✅ Matched ({len(skill_comp['matched'])})",
        f"⚠️ Missing ({len(skill_comp['missing'])})",
        f"➕ Additional ({len(skill_comp['additional'])})",
    ])

    with tab1:
        st.markdown(
            '<div class="result-section">',
            unsafe_allow_html=True,
        )
        st.markdown("Skills found in **both** your resume and the job description:")
        render_skill_tags(skill_comp['matched_details'], 'skill-matched')
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown(
            '<div class="result-section">',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Skills mentioned in the **job description** but "
            "**not found** in your resume:"
        )
        render_skill_tags(skill_comp['missing_details'], 'skill-missing')
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown(
            '<div class="result-section">',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Skills in your **resume** that are **not required** "
            "by this job description:"
        )
        render_skill_tags(skill_comp['additional_details'], 'skill-additional')
        st.markdown("</div>", unsafe_allow_html=True)

    # ── F. Skills breakdown chart ──
    st.markdown("### 📊 Job Description Skills Breakdown")
    render_skills_chart(skill_comp)

    st.markdown("---")

    # ── C. Strengths ──
    st.markdown("### 💪 Resume Strengths")
    for s in gap.get('strengths', []):
        st.markdown(f"""
        <div class="strength-card">
            <div class="card-title">✅ {s['title']}</div>
            <div class="card-detail">{s['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── D. Areas for Improvement ──
    st.markdown("### 🔧 Areas for Improvement")
    for w in gap.get('weaknesses', []):
        st.markdown(f"""
        <div class="weakness-card">
            <div class="card-title">⚠️ {w['title']}</div>
            <div class="card-detail">{w['detail']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── E. Recommendations ──
    st.markdown("### 💡 Recommendations")
    for i, rec in enumerate(recs, 1):
        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-title">{i}. {rec['title']}</div>
            <div class="rec-explanation">{rec['explanation']}</div>
            <div class="rec-action">→ {rec['action']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── G. Roast My Resume ──
    st.markdown("### 🔥 Roast My Resume")
    st.caption(
        "An honest, witty, constructive critique of your resume. "
        "Take it with a grain of humor!"
    )
    for roast in roasts:
        st.markdown(
            f'<div class="roast-card">{roast}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── H. Download Report ──
    st.markdown("### 📥 Download Report")
    try:
        report_bytes = generate_report(results)
        st.download_button(
            label="📄 Download PDF Analysis Report",
            data=report_bytes,
            file_name="resume_roast_analysis.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Failed to generate PDF report: {e}")

    # Summary
    st.markdown("---")
    st.markdown(
        f'<div class="result-section">'
        f'<h3>📝 Summary</h3>'
        f'<p>{gap.get("summary", "")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
