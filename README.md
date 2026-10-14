# Resume Skill Analyzer

[![Python](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![spaCy](https://img.shields.io/badge/spaCy-3.7%2B-09A3D5?logo=spacy&logoColor=white)](https://spacy.io/)

An intelligent Natural Language Processing (NLP) web application that parses, extracts, and categorizes technical skills from resumes in **PDF** and **DOCX** formats.

---

## Overview

In technical recruitment and automated talent screening, extracting technical competencies accurately and quickly is critical. **Resume Skill Analyzer** bridges raw resume documents and structured talent insights by combining linguistic preprocessing, regex normalization, and spaCy's high-performance entity matching.

### Key Highlights
- **Authentic PDF Document Rendering:** Retains full visual layout, tables, formatting, and typography page-by-page using `pypdfium2` — no text loss or visual distortion.
- **Categorized Technical Competencies:** Automatically classifies extracted skills into 7 core technical domains.
- **Live Search & Metrics:** Instant skill count badge, domain breakdowns, and real-time keyword filtering.
- **Pre-loaded Test Resumes:** Built-in sample resumes (Full-Stack, AI & Data Science, DevOps, and Non-Technical) for instant one-click demonstration.

---

## 7 Competency Domains

| Domain | Example Extracted Skills |
|---|---|
| **Programming Languages** | Python, Java, C++, TypeScript, JavaScript, Go, SQL, Bash, Rust, Kotlin |
| **Web Development** | React, Next.js, Node.js, FastAPI, Django, Flask, Express, GraphQL, Tailwind CSS |
| **Databases** | PostgreSQL, MongoDB, Redis, MySQL, SQLite, Supabase |
| **AI / Machine Learning** | Machine Learning, Deep Learning, NLP, PyTorch, TensorFlow, Scikit-learn, Hugging Face |
| **Data Science** | Pandas, NumPy, Matplotlib, Seaborn, Power BI, Statistics |
| **Tools & Platforms** | Git, GitHub, Docker, VS Code, Linux, Postman, Jira, Figma |
| **Cloud & DevOps** | AWS, Azure, GCP, Kubernetes, CI/CD, GitHub Actions, Terraform, Nginx |

---

## Project Architecture

```text
resume-skill-analyzer/
│
├── app.py                   # Streamlit web interface & visual document inspector
├── nlp_processor.py         # spaCy NLP pipeline, text cleaning & phrase matcher
├── resume_parser.py         # Multi-format document parser (PDF & DOCX)
├── skills.py                # Predefined technical skills taxonomy & alias dictionary
├── generate_test_resumes.py # Generator for realistic test PDF & DOCX resumes
├── test_extractor.py        # Automated test suite (10 unit tests)
├── requirements.txt         # Package dependencies
├── run_app.bat              # Windows batch launcher
├── run_app.ps1              # PowerShell launcher
└── README.md                # Project documentation
```

---

## Tech Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
- **NLP Engine:** [spaCy](https://spacy.io/) (`en_core_web_sm` / `PhraseMatcher`)
- **Document Parsing:** [pdfplumber](https://github.com/jsvine/pdfplumber), [pypdf](https://github.com/py-pdf/pypdf), [python-docx](https://python-docx.readthedocs.io/)
- **High-Res PDF Page Rendering:** [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
- **Data Handling:** [Pandas](https://pandas.pydata.org/)