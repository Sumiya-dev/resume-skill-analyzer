"""
app.py
Resume Skill Extractor — Colorful & Bright Modern UI.
Side-by-side layout:
- Left: Authentic original PDF resume rendered visually as it is (without converting to text).
- Right: Only extracted technical skills, neatly organized by the 7 domains with vibrant accent colors.
"""

import base64
import html
import io
import os
from typing import Dict, List, Optional
from PIL import Image
import pypdfium2 as pdfium
import streamlit as st

from nlp_processor import extract_skills_from_text
from resume_parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
    parse_resume,
)

# Page configuration
st.set_page_config(
    page_title="Resume Skill Extractor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 7 Technical Domains Configuration with Vibrant & Bright Color Schemes
CATEGORIES_DISPLAY_CONFIG = [
    {
        "internal_key": "Programming Languages",
        "display_name": "Programming",
        "icon": "💻",
        "header_color": "#1d4ed8",
        "accent_gradient": "linear-gradient(90deg, #2563eb, #38bdf8)",
        "pill_bg": "#eff6ff",
        "pill_border": "#93c5fd",
        "pill_text": "#1e40af",
        "badge_bg": "#dbeafe",
        "badge_text": "#1e40af",
    },
    {
        "internal_key": "Web Development",
        "display_name": "Web Development",
        "icon": "🌐",
        "header_color": "#047857",
        "accent_gradient": "linear-gradient(90deg, #059669, #34d399)",
        "pill_bg": "#ecfdf5",
        "pill_border": "#6ee7b7",
        "pill_text": "#065f46",
        "badge_bg": "#d1fae5",
        "badge_text": "#065f46",
    },
    {
        "internal_key": "Databases",
        "display_name": "Databases",
        "icon": "🗄️",
        "header_color": "#b45309",
        "accent_gradient": "linear-gradient(90deg, #d97706, #fbbf24)",
        "pill_bg": "#fffbeb",
        "pill_border": "#fcd34d",
        "pill_text": "#92400e",
        "badge_bg": "#fef3c7",
        "badge_text": "#92400e",
    },
    {
        "internal_key": "AI/ML",
        "display_name": "AI / Machine Learning",
        "icon": "🧠",
        "header_color": "#6d28d9",
        "accent_gradient": "linear-gradient(90deg, #7c3aed, #a78bfa)",
        "pill_bg": "#f5f3ff",
        "pill_border": "#c4b5fd",
        "pill_text": "#5b21b6",
        "badge_bg": "#ede9fe",
        "badge_text": "#5b21b6",
    },
    {
        "internal_key": "Data Science",
        "display_name": "Data Science",
        "icon": "📊",
        "header_color": "#be185d",
        "accent_gradient": "linear-gradient(90deg, #db2777, #f472b6)",
        "pill_bg": "#fdf2f8",
        "pill_border": "#f9a8d4",
        "pill_text": "#9d174d",
        "badge_bg": "#fce7f3",
        "badge_text": "#9d174d",
    },
    {
        "internal_key": "Tools/Platforms",
        "display_name": "Tools",
        "icon": "🛠️",
        "header_color": "#c2410c",
        "accent_gradient": "linear-gradient(90deg, #ea580c, #fb923c)",
        "pill_bg": "#fff7ed",
        "pill_border": "#fdba74",
        "pill_text": "#9a3412",
        "badge_bg": "#ffedd5",
        "badge_text": "#9a3412",
    },
    {
        "internal_key": "Cloud/DevOps",
        "display_name": "Cloud / DevOps",
        "icon": "☁️",
        "header_color": "#0e7490",
        "accent_gradient": "linear-gradient(90deg, #0891b2, #38bdf8)",
        "pill_bg": "#ecfeff",
        "pill_border": "#67e8f9",
        "pill_text": "#155e75",
        "badge_bg": "#cffafe",
        "badge_text": "#155e75",
    },
]

# Sample Resumes Dictionary
SAMPLE_RESUMES = {
    "None (Use uploaded file)": None,
    "Software Engineer (Full-Stack) — Alex Mercer": {
        "pdf_path": "sample_resumes/sample_software_engineer_resume.pdf",
        "docx_path": "sample_resumes/sample_software_engineer_resume.docx",
        "label": "Software Engineer — Alex Mercer",
    },
    "AI & Data Science Specialist — Sarah Jenkins": {
        "pdf_path": "sample_resumes/sample_ai_engineer_resume.pdf",
        "docx_path": None,
        "label": "AI & Data Science — Sarah Jenkins",
    },
    "DevOps & Cloud Engineer — David Clark": {
        "pdf_path": "sample_resumes/sample_devops_engineer_resume.pdf",
        "docx_path": None,
        "label": "DevOps & Cloud — David Clark",
    },
    "Empty / Non-Technical Document": {
        "pdf_path": "sample_resumes/empty_sample_resume.pdf",
        "docx_path": "sample_resumes/empty_sample_resume.docx",
        "label": "Non-Technical Sample (0 Skills)",
    },
}

# Custom Bright & Colorful CSS Styling
st.markdown(
    """<style>
/* Global Canvas & Modern Bright Palette */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 45%, #f0fdf4 100%) !important;
    color: #0f172a !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}

/* Remove default sidebar for full-width workspace */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] {
    display: none !important;
}

/* Container Spacing */
.main .block-container {
    max-width: 1420px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
}

/* Vibrant Primary Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 0.65rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.96rem !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4338ca 0%, #6d28d9 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* Secondary Button Style */
.secondary-btn .stButton > button {
    background: #ffffff !important;
    color: #4f46e5 !important;
    border: 1.5px solid #c7d2fe !important;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.12) !important;
}
.secondary-btn .stButton > button:hover {
    background: #eef2ff !important;
    border-color: #818cf8 !important;
    color: #3730a3 !important;
    transform: translateY(-1px) !important;
}

/* Download Button Styling */
.stDownloadButton > button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 2px 5px rgba(15, 23, 42, 0.05) !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #1e293b !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background-color: #ffffff !important;
    border: 2px dashed #818cf8 !important;
    border-radius: 12px !important;
    padding: 1.4rem !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.08) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #4f46e5 !important;
    background-color: #fcfdff !important;
}
[data-testid="stFileUploader"] section {
    background-color: transparent !important;
    padding: 0 !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background-color: #ffffff !important;
    border: 1.5px solid #c7d2fe !important;
    border-radius: 8px !important;
    color: #0f172a !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
}

/* Pane Header Styling */
.pane-header-box {
    background: #ffffff;
    border-radius: 10px 10px 0 0;
    border: 1.5px solid #cbd5e1;
    border-bottom: 2px solid #e2e8f0;
    padding: 12px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(15, 23, 42, 0.03);
}
.pane-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 8px;
}
.pane-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 11px;
    border-radius: 9999px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

/* Left Pane: PDF Viewer Workbench Container */
.pdf-viewer-workbench {
    background: #e2e8f0;
    border: 1.5px solid #cbd5e1;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 16px;
    height: 750px;
    max-height: 750px;
    overflow-y: auto;
    box-shadow: inset 0 2px 8px rgba(15, 23, 42, 0.08);
}
.pdf-page-card {
    background: #ffffff;
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.16), 0 2px 6px rgba(15, 23, 42, 0.08);
    margin-bottom: 20px;
    border: 1px solid #94a3b8;
    overflow: hidden;
}
.pdf-page-header {
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    padding: 6px 14px;
    font-size: 0.74rem;
    color: #475569;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pdf-page-img {
    width: 100%;
    display: block;
    height: auto;
}

/* Right Pane: Skills Scroll Container */
.skills-container-box {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 16px;
    height: 750px;
    max-height: 750px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    box-shadow: inset 0 2px 6px rgba(15, 23, 42, 0.03);
}

/* Sleek Scrollbars */
.skills-container-box::-webkit-scrollbar,
.pdf-viewer-workbench::-webkit-scrollbar {
    width: 8px;
}
.skills-container-box::-webkit-scrollbar-track,
.pdf-viewer-workbench::-webkit-scrollbar-track {
    background: #e2e8f0;
    border-radius: 4px;
}
.skills-container-box::-webkit-scrollbar-thumb,
.pdf-viewer-workbench::-webkit-scrollbar-thumb {
    background: #94a3b8;
    border-radius: 4px;
}
.skills-container-box::-webkit-scrollbar-thumb:hover,
.pdf-viewer-workbench::-webkit-scrollbar-thumb:hover {
    background: #64748b;
}

/* Category Cards */
.cat-card {
    background: #ffffff;
    border-radius: 10px;
    border: 1.5px solid #e2e8f0;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.cat-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.07);
}
.cat-accent-bar {
    height: 5px;
    width: 100%;
}
.cat-card-body {
    padding: 14px 16px;
}
.cat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.cat-title-text {
    font-size: 0.94rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
}
.cat-count-pill {
    font-size: 0.74rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 9999px;
    letter-spacing: 0.02em;
}

/* Bright & Colorful Skill Badges */
.skill-pill {
    display: inline-flex;
    align-items: center;
    padding: 5px 12px;
    margin: 3px 6px 4px 0;
    border-radius: 8px;
    font-size: 0.84rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 1.35;
    transition: all 0.15s ease;
    cursor: default;
}
.skill-pill:hover {
    transform: translateY(-2px);
    filter: brightness(0.96);
}

.empty-domain-notice {
    font-size: 0.83rem;
    color: #94a3b8;
    font-weight: 500;
    font-style: italic;
    padding: 4px 0;
}

/* Error Banner */
.custom-error-box {
    background-color: #fef2f2;
    border: 1.5px solid #fecaca;
    color: #b91c1c;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.92rem;
    font-weight: 600;
    margin-bottom: 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Streamlit Header / Footer Cleanups */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}
footer {
    display: none !important;
}
</style>""",
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize session state variables."""
    if "analyzed" not in st.session_state:
        st.session_state["analyzed"] = False
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = ""
    if "source_name" not in st.session_state:
        st.session_state["source_name"] = ""
    if "file_bytes" not in st.session_state:
        st.session_state["file_bytes"] = None
    if "file_type" not in st.session_state:
        st.session_state["file_type"] = "pdf"
    if "extraction_result" not in st.session_state:
        st.session_state["extraction_result"] = None
    if "error_message" not in st.session_state:
        st.session_state["error_message"] = None


@st.cache_data(show_spinner=False)
def render_pdf_to_base64_images(pdf_bytes: bytes) -> List[str]:
    """
    Render all pages of a PDF document to crisp, high-resolution JPEG base64 strings using pypdfium2.
    Ensures the original PDF visual appearance is preserved without converting to text.
    """
    try:
        pdf = pdfium.PdfDocument(pdf_bytes)
        b64_pages = []
        for page in pdf:
            # 2.0x scale gives crisp retina rendering for text, lines, and formatting
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=88)
            b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            b64_pages.append(b64_str)
        return b64_pages
    except Exception as e:
        st.error(f"Error rendering PDF pages: {str(e)}")
        return []


def render_landing_page():
    """Render the bright, colorful SaaS landing page."""
    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)

    # Hero Banner
    hero_html = (
        '<div style="text-align: center; margin-bottom: 34px;">'
        '<div style="display: inline-flex; align-items: center; gap: 7px; background: #eef2ff; color: #4f46e5; border: 1.5px solid #c7d2fe; padding: 5px 16px; border-radius: 9999px; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(79, 70, 229, 0.1);">'
        '⚡ NLP Skill Analyzer & Visual Document Inspector'
        '</div>'
        '<h1 style="font-size: 2.7rem; font-weight: 800; letter-spacing: -0.03em; margin: 0 0 10px 0; background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 35%, #7c3aed 70%, #db2777 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">'
        'Resume Technical Skill Extractor</h1>'
        '<p style="color: #475569; font-size: 1.12rem; max-width: 680px; margin: 0 auto; line-height: 1.55;">'
        'Inspect your original PDF resume side-by-side with automated NLP technical skill detection and categorization across 7 domains.'
        '</p>'
        '</div>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

    if st.session_state.get("error_message"):
        err_msg = html.escape(st.session_state["error_message"])
        st.markdown(
            f'<div class="custom-error-box">⚠️ <span>{err_msg}</span></div>',
            unsafe_allow_html=True,
        )
        st.session_state["error_message"] = None

    # Main Card
    col_upload, col_sample = st.columns([1.5, 1.1], gap="large")

    with col_upload:
        st.markdown(
            '<div style="font-size: 0.92rem; text-transform: uppercase; letter-spacing: 0.05em; color: #4338ca; font-weight: 700; margin-bottom: 8px;">Option 1: Upload Your Resume</div>',
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            help="Select a PDF (.pdf) for authentic visual document view, or DOCX (.docx).",
        )
        st.markdown(
            '<div style="font-size: 0.82rem; color: #64748b; margin-top: 6px;">💡 <b>PDF Recommended:</b> Preserves exact visual layout, formatting, typography, and structure.</div>',
            unsafe_allow_html=True,
        )

    with col_sample:
        st.markdown(
            '<div style="font-size: 0.92rem; text-transform: uppercase; letter-spacing: 0.05em; color: #4338ca; font-weight: 700; margin-bottom: 8px;">Option 2: Try A Pre-Built Sample</div>',
            unsafe_allow_html=True,
        )
        sample_choice = st.selectbox(
            "Choose Sample",
            options=list(SAMPLE_RESUMES.keys()),
            index=0,
            label_visibility="collapsed",
            help="Select a pre-built sample resume to test immediately.",
        )
        if sample_choice != "None (Use uploaded file)":
            st.markdown(
                '<div style="font-size: 0.82rem; color: #059669; font-weight: 600; margin-top: 8px; background: #ecfdf5; border: 1px solid #a7f3d0; padding: 7px 12px; border-radius: 6px;">'
                '✓ Pre-loaded PDF ready for instant visual analysis'
                '</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div style="height: 18px;"></div>', unsafe_allow_html=True)

    # Action Button
    col_btn, _ = st.columns([1.5, 3.5])
    with col_btn:
        analyze_clicked = st.button("🚀 Analyze Resume & Skills", use_container_width=True)

    # Category Showcase Cards
    st.markdown('<div style="height: 36px;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: center; margin-bottom: 16px;">'
        '<span style="font-size: 0.85rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em;">7 Supported Technical Competency Domains</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    
    showcase_cols = st.columns(7)
    for idx, cat in enumerate(CATEGORIES_DISPLAY_CONFIG):
        with showcase_cols[idx]:
            st.markdown(
                f'<div style="background: #ffffff; border: 1px solid {cat["pill_border"]}; border-radius: 8px; padding: 12px 6px; text-align: center; box-shadow: 0 2px 6px rgba(15,23,42,0.03);">'
                f'<div style="font-size: 1.4rem; margin-bottom: 4px;">{cat["icon"]}</div>'
                f'<div style="font-size: 0.78rem; font-weight: 700; color: {cat["header_color"]}; line-height: 1.2;">{cat["display_name"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if analyze_clicked:
        resume_text = ""
        source_name = ""
        file_bytes = None
        file_type = "pdf"

        if uploaded_file is not None:
            source_name = uploaded_file.name
            file_bytes = uploaded_file.getvalue()
            if source_name.lower().endswith(".pdf"):
                file_type = "pdf"
                with st.spinner("Extracting text from PDF..."):
                    extracted_text, parse_err = extract_text_from_pdf(io.BytesIO(file_bytes))
            elif source_name.lower().endswith(".docx"):
                file_type = "docx"
                with st.spinner("Extracting text from DOCX..."):
                    extracted_text, parse_err = extract_text_from_docx(io.BytesIO(file_bytes))
            else:
                parse_err = "Unsupported file type. Please upload a PDF or DOCX file."

            if parse_err:
                st.session_state["error_message"] = f"Document Error: {parse_err}"
                st.rerun()
            resume_text = extracted_text

        elif sample_choice and sample_choice != "None (Use uploaded file)":
            sample_info = SAMPLE_RESUMES[sample_choice]
            source_name = sample_info["label"]
            pdf_path = sample_info["pdf_path"]

            if os.path.exists(pdf_path):
                file_type = "pdf"
                with open(pdf_path, "rb") as f:
                    file_bytes = f.read()
                with st.spinner("Parsing sample PDF..."):
                    extracted_text, parse_err = extract_text_from_pdf(io.BytesIO(file_bytes))
                if parse_err:
                    st.session_state["error_message"] = f"Sample Error: {parse_err}"
                    st.rerun()
                resume_text = extracted_text
            else:
                st.session_state["error_message"] = f"Sample file not found: {pdf_path}"
                st.rerun()
        else:
            st.session_state["error_message"] = "Please upload a resume file or select a sample resume."
            st.rerun()

        if not resume_text or not resume_text.strip():
            st.session_state["error_message"] = "The document contains no readable text or is empty."
            st.rerun()

        with st.spinner("Analyzing technical skills with NLP pipeline..."):
            result = extract_skills_from_text(resume_text)

        st.session_state["analyzed"] = True
        st.session_state["resume_text"] = resume_text
        st.session_state["source_name"] = source_name
        st.session_state["file_bytes"] = file_bytes
        st.session_state["file_type"] = file_type
        st.session_state["extraction_result"] = result
        st.rerun()


def render_results_page():
    """
    Render the clean, colorful two-column view:
    - Left Column: Authentic resume PDF visually as it is (without converting to text).
    - Right Column: ONLY extracted technical skills grouped by the 7 categories.
    """
    result = st.session_state["extraction_result"]
    source_name = st.session_state["source_name"]
    file_bytes = st.session_state["file_bytes"]
    file_type = st.session_state["file_type"]
    resume_text = st.session_state["resume_text"]

    categorized_skills = result["categorized_skills"]
    total_skills = result["total_skills"]

    # Top Navigation & Header
    top_bar_col1, top_bar_col2 = st.columns([3.8, 1.2], gap="large")
    with top_bar_col1:
        escaped_source = html.escape(str(source_name))
        header_html = (
            f'<div style="margin-bottom: 14px;">'
            f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">'
            f'<span style="background: #eef2ff; color: #4f46e5; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 9999px; text-transform: uppercase; border: 1.5px solid #c7d2fe;">Analysis Completed</span>'
            f'<span style="color: #64748b; font-size: 0.88rem;">Document: <b style="color: #0f172a;">{escaped_source}</b></span>'
            f'<span style="background: #dbeafe; color: #1e40af; font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 9999px;">🎯 {total_skills} Skills Extracted</span>'
            f'</div>'
            f'<h1 style="font-size: 1.95rem; margin: 0; font-weight: 800; letter-spacing: -0.02em; background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 50%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">'
            f'Resume Skills & Document Inspector</h1>'
            f'</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

    with top_bar_col2:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🔄 Analyze Another Resume", use_container_width=True):
            st.session_state["analyzed"] = False
            st.session_state["resume_text"] = ""
            st.session_state["source_name"] = ""
            st.session_state["file_bytes"] = None
            st.session_state["extraction_result"] = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Two-Column Workspace Layout (Left: PDF as it is | Right: ONLY Skills)
    col_pdf, col_skills = st.columns([1.1, 1.0], gap="large")

    # ==========================================
    # LEFT COLUMN: Authentic Resume PDF Viewer
    # ==========================================
    with col_pdf:
        # Pane Header
        left_header = (
            f'<div class="pane-header-box">'
            f'<div class="pane-title"><span>📄</span> Original Resume Document</div>'
            f'<div class="pane-badge" style="background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;">'
            f'<span>●</span> AUTHENTIC PDF VIEW'
            f'</div>'
            f'</div>'
        )
        st.markdown(left_header, unsafe_allow_html=True)

        # PDF Visual Rendering
        if file_type == "pdf" and file_bytes:
            # Render PDF pages to high-resolution JPEG base64 strings
            b64_pages = render_pdf_to_base64_images(file_bytes)
            num_pages = len(b64_pages)

            if num_pages > 0:
                pages_html_list = []
                for idx, b64_img in enumerate(b64_pages, start=1):
                    page_html = (
                        f'<div class="pdf-page-card">'
                        f'<div class="pdf-page-header">'
                        f'<span>PAGE {idx} OF {num_pages}</span>'
                        f'<span style="color: #64748b; font-weight: 600;">High-Resolution (2.0x)</span>'
                        f'</div>'
                        f'<img class="pdf-page-img" src="data:image/jpeg;base64,{b64_img}" alt="Resume Page {idx}" />'
                        f'</div>'
                    )
                    pages_html_list.append(page_html)

                left_pane_content = (
                    f'<div class="pdf-viewer-workbench">{"".join(pages_html_list)}</div>'
                )
                st.markdown(left_pane_content, unsafe_allow_html=True)
            else:
                st.warning("Could not render PDF pages visually.")

            # Quick PDF download button below workbench
            st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
            st.download_button(
                label="📥 Download Original PDF Resume",
                data=file_bytes,
                file_name=source_name if source_name.lower().endswith(".pdf") else "resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        elif file_type == "docx":
            # For DOCX uploads, present formatted document view
            st.markdown(
                '<div class="pdf-viewer-workbench">'
                '<div style="background: #fffbeb; border: 1px solid #fde68a; color: #b45309; padding: 10px 14px; border-radius: 6px; font-size: 0.82rem; margin-bottom: 14px; font-weight: 500;">'
                'ℹ️ <b>DOCX Document Uploaded:</b> For native visual PDF page rendering, upload in .pdf format. Formatted document content shown below:'
                '</div>'
                f'<div style="background: #ffffff; padding: 24px; border-radius: 8px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); font-family: ui-monospace, monospace; font-size: 0.85rem; line-height: 1.6; white-space: pre-wrap; color: #334155; border: 1px solid #cbd5e1;">'
                f'{html.escape(resume_text)}'
                '</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            if file_bytes:
                st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download DOCX Document",
                    data=file_bytes,
                    file_name=source_name if source_name.lower().endswith(".docx") else "resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
        else:
            st.info("No document available for preview.")

    # ==========================================
    # RIGHT COLUMN: ONLY Extracted Skills
    # ==========================================
    with col_skills:
        # Pane Header
        right_header = (
            f'<div class="pane-header-box">'
            f'<div class="pane-title"><span>⚡</span> Extracted Technical Skills</div>'
            f'<div class="pane-badge" style="background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe;">'
            f'{total_skills} Skills Found'
            f'</div>'
            f'</div>'
        )
        st.markdown(right_header, unsafe_allow_html=True)

        # Quick Live Search Filter
        skill_search = st.text_input(
            "Filter skills",
            placeholder="🔍 Type to filter skills (e.g. Python, React, Docker, AWS)...",
            label_visibility="collapsed",
            key="skill_filter_query",
        ).strip().lower()

        # Build colorful category cards
        cards_html_list = []
        for cat in CATEGORIES_DISPLAY_CONFIG:
            internal_key = cat["internal_key"]
            display_name = cat["display_name"]
            icon = cat["icon"]
            header_color = cat["header_color"]
            accent_grad = cat["accent_gradient"]
            pill_bg = cat["pill_bg"]
            pill_border = cat["pill_border"]
            pill_text = cat["pill_text"]
            badge_bg = cat["badge_bg"]
            badge_text = cat["badge_text"]

            raw_skills_in_cat = categorized_skills.get(internal_key, [])
            if skill_search:
                skills_in_cat = [s for s in raw_skills_in_cat if skill_search in s.lower()]
            else:
                skills_in_cat = raw_skills_in_cat
            cat_count = len(skills_in_cat)

            if skills_in_cat:
                pills_html = "".join([
                    f'<span class="skill-pill" style="background: {pill_bg}; border: 1.5px solid {pill_border}; color: {pill_text}; box-shadow: 0 2px 5px rgba(0,0,0,0.03);" '
                    f'title="{html.escape(s)}">{html.escape(s)}</span>'
                    for s in skills_in_cat
                ])
                count_badge = f'<span class="cat-count-pill" style="background: {badge_bg}; color: {badge_text};">{cat_count} skills</span>'
            else:
                notice = "No matching skills found" if skill_search and raw_skills_in_cat else "No technical skills detected in this domain"
                pills_html = f'<div class="empty-domain-notice">{notice}</div>'
                count_badge = '<span class="cat-count-pill" style="background: #f1f5f9; color: #94a3b8;">0</span>'

            card_html = (
                f'<div class="cat-card">'
                f'<div class="cat-accent-bar" style="background: {accent_grad};"></div>'
                f'<div class="cat-card-body">'
                f'<div class="cat-header">'
                f'<div class="cat-title-text" style="color: {header_color};"><span>{icon}</span> <span>{display_name}</span></div>'
                f'{count_badge}'
                f'</div>'
                f'<div>{pills_html}</div>'
                f'</div>'
                f'</div>'
            )
            cards_html_list.append(card_html)

        right_pane_content = f'<div class="skills-container-box">{"".join(cards_html_list)}</div>'
        st.markdown(right_pane_content, unsafe_allow_html=True)


def main():
    init_session_state()
    if not st.session_state["analyzed"]:
        render_landing_page()
    else:
        render_results_page()


if __name__ == "__main__":
    main()
