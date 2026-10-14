"""
nlp_processor.py
NLP preprocessing and technical skill extraction module using spaCy and rule-based NLP techniques.
"""

import re
from typing import Any, Dict, List, Set, Tuple
import spacy
from spacy.matcher import PhraseMatcher

from skills import (
    SKILL_ALIASES,
    SKILL_CATEGORIES,
    get_all_skills,
    get_category_for_skill,
)

# Global cache for the loaded spaCy model and matcher
_NLP_MODEL = None
_PHRASE_MATCHER = None


def load_spacy_model():
    """
    Load the English spaCy model.
    Falls back gracefully to spacy.blank('en') if en_core_web_sm is not available.
    """
    global _NLP_MODEL
    if _NLP_MODEL is not None:
        return _NLP_MODEL

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        try:
            # Attempt to download automatically
            from spacy.cli import download

            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            # Offline / fallback: use blank English model with sentencizer
            nlp = spacy.blank("en")
            if "sentencizer" not in nlp.pipe_names:
                nlp.add_pipe("sentencizer")

    _NLP_MODEL = nlp
    return _NLP_MODEL


def clean_text(raw_text: str) -> str:
    """
    Clean and normalize raw resume text:
    - Normalizes line breaks and whitespace
    - Removes URL links, email addresses, and phone numbers
    - Removes strange non-printable symbols while preserving code/skill symbols (+, #, ., /, -)
    """
    if not raw_text:
        return ""

    text = raw_text

    # Normalize various unicode spaces and bullet symbols
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u00B7\u25AA\u25AB\u2013\u2014]", " ", text)
    text = re.sub(r"[\t\r\f\v]", " ", text)

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text, flags=re.IGNORECASE)

    # Remove email addresses
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)

    # Remove phone numbers (various formats)
    text = re.sub(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", " ", text)

    # Replace multiple spaces with a single space, but preserve newlines
    lines = [re.sub(r"[ ]+", " ", line).strip() for line in text.split("\n")]
    cleaned_lines = [line for line in lines if line]

    return "\n".join(cleaned_lines)


def get_phrase_matcher(nlp) -> PhraseMatcher:
    """
    Build and cache a spaCy PhraseMatcher loaded with all skill patterns.
    """
    global _PHRASE_MATCHER
    if _PHRASE_MATCHER is not None:
        return _PHRASE_MATCHER

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

    # Group patterns by category
    category_patterns: Dict[str, List[Any]] = {cat: [] for cat in SKILL_CATEGORIES}

    # Add canonical skills from SKILL_CATEGORIES
    for category, skill_list in SKILL_CATEGORIES.items():
        for skill in skill_list:
            # Skip very short ambiguous skills like 'C' or 'R' or 'Go' from raw phrase matcher
            # (they will be handled by context-aware regex to prevent false positives)
            if skill.lower() in {"c", "r", "go", "ai"}:
                continue
            doc = nlp.make_doc(skill)
            category_patterns[category].append(doc)

    # Add aliases
    for alias, (canonical_name, category) in SKILL_ALIASES.items():
        if alias in {"c", "r", "go", "ai"}:
            continue
        doc = nlp.make_doc(alias)
        category_patterns[category].append(doc)

    for category, docs in category_patterns.items():
        if docs:
            matcher.add(category, docs)

    _PHRASE_MATCHER = matcher
    return _PHRASE_MATCHER


def extract_special_symbol_skills(text: str) -> Dict[str, Tuple[str, str, int]]:
    """
    Extract skills that contain symbols like '+', '#', '/', or single letters
    where standard tokenizers may split or introduce noise (e.g., C++, C#, CI/CD, .NET).
    Returns a dict mapping canonical_name -> (canonical_name, category, count).
    """
    results: Dict[str, Tuple[str, str, int]] = {}

    # Define precise regex patterns with lookaround/word boundaries
    special_patterns = [
        # C++
        (r"(?i)(?:\bC\+\+|\bc\s*\+\+)", "C++", "Programming Languages"),
        # C#
        (r"(?i)(?:\bC\#|\bc\s*\#|\bcsharp\b)", "C#", "Programming Languages"),
        # .NET / ASP.NET / ASP.NET Core
        (r"(?i)\basp\.net\s+core\b", "ASP.NET Core", "Web Development"),
        (r"(?i)\basp\.net\b", "ASP.NET", "Web Development"),
        (r"(?i)(?:\b\.net\s+core\b|\b\.net\b)", ".NET", "Web Development"),
        # CI/CD
        (r"(?i)\bci\s*/\s*cd\b|\bcicd\b", "CI/CD", "Cloud/DevOps"),
        # Node.js
        (r"(?i)\bnode(?:\.js)?\b", "Node.js", "Web Development"),
        # Vue.js
        (r"(?i)\bvue(?:\.js)?\b", "Vue.js", "Web Development"),
        # Next.js
        (r"(?i)\bnext(?:\.js)?\b", "Next.js", "Web Development"),
        # React.js
        (r"(?i)\breact(?:\.js)?\b", "React.js", "Web Development"),
        # Scikit-learn
        (r"(?i)\bscikit-learn\b|\bsklearn\b", "Scikit-learn", "AI/ML"),
        # Power BI
        (r"(?i)\bpower\s*bi\b", "Power BI", "Data Science"),
        # REST API / RESTful API
        (r"(?i)\brest(?:ful)?\s*(?:api|apis)\b", "REST API", "Web Development"),
    ]

    for pattern, canonical_name, category in special_patterns:
        matches = re.findall(pattern, text)
        if matches:
            count = len(matches)
            results[canonical_name] = (canonical_name, category, count)

    # Ambiguous short single-letter / small skills: C, R, Go, AI
    # Only match if in a programming/skills context or list: e.g. "Languages: C, Python" or "C/C++"
    # Match "C" programming
    c_pattern = r"(?i)(?:\bC\s*(?:programming|language)\b|\b(?:languages?|skills?|technologies?)[^.\n]*?\bC\b|\bC\s*/\s*C\+\+)"
    c_matches = re.findall(c_pattern, text)
    if c_matches and "C" not in results:
        results["C"] = ("C", "Programming Languages", len(c_matches))

    # Match "R" programming
    r_pattern = r"(?i)(?:\bR\s*(?:programming|language|scripting)\b|\b(?:languages?|skills?|tools?)[^.\n]*?\bR\b|\bPython\s*(?:and|/|,)\s*R\b)"
    r_matches = re.findall(r_pattern, text)
    if r_matches and "R" not in results:
        results["R"] = ("R", "Programming Languages", len(r_matches))

    # Match "Go" / Golang
    go_pattern = r"(?i)(?:\bgolang\b|\bGo\s*(?:language|programming|developer|backend)\b)"
    go_matches = re.findall(go_pattern, text)
    if go_matches and "Go" not in results:
        results["Go"] = ("Go", "Programming Languages", len(go_matches))

    # Match "AI" when with ML or explicit
    ai_pattern = r"(?i)(?:\bAI\s*/\s*ML\b|\bAI\s*&\s*ML\b|\bArtificial Intelligence\b|\bAI\s+Engineer\b|\bAI\s+Researcher\b)"
    ai_matches = re.findall(ai_pattern, text)
    if ai_matches and "Artificial Intelligence" not in results:
        results["Artificial Intelligence"] = ("Artificial Intelligence", "AI/ML", len(ai_matches))

    return results


def extract_skills_from_text(raw_text: str) -> Dict[str, Any]:
    """
    Main NLP function to extract and categorize technical skills from resume text.

    Returns a rich dictionary containing:
    - total_skills: Total count of unique detected skills
    - category_counts: Dict mapping category -> count of detected skills
    - categorized_skills: Dict mapping category -> list of canonical skill names
    - detected_skills_detail: List of dicts with skill, category, and frequency
    - cleaned_text: Cleaned input text
    - statistics: NLP text metrics (word count, sentence count, vocab count)
    - spacy_model_used: Name of the spaCy model used
    """
    cleaned = clean_text(raw_text)
    if not cleaned.strip():
        return {
            "total_skills": 0,
            "category_counts": {cat: 0 for cat in SKILL_CATEGORIES},
            "categorized_skills": {cat: [] for cat in SKILL_CATEGORIES},
            "detected_skills_detail": [],
            "cleaned_text": "",
            "statistics": {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "vocabulary_size": 0,
            },
            "spacy_model_used": "none",
        }

    nlp = load_spacy_model()
    doc = nlp(cleaned)
    matcher = get_phrase_matcher(nlp)

    # Skill tracking: canonical_name -> {"category": category, "count": count}
    extracted_skills_map: Dict[str, Dict[str, Any]] = {}

    # 1. Match special symbol skills & sensitive acronyms (C++, C#, CI/CD, .NET, Node.js, etc.)
    special_matches = extract_special_symbol_skills(cleaned)
    for canonical_name, (name, category, count) in special_matches.items():
        extracted_skills_map[canonical_name] = {
            "category": category,
            "count": count,
        }

    # 2. Run spaCy PhraseMatcher
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        matched_text = span.text.strip().lower()

        # Resolve alias to canonical skill name and category
        if matched_text in SKILL_ALIASES:
            canonical_name, category = SKILL_ALIASES[matched_text]
        else:
            # Match directly against canonical skill
            category = nlp.vocab.strings[match_id]
            canonical_name = span.text.strip().title()
            # Check if canonical exists in SKILL_CATEGORIES
            found_canonical = None
            for c_skill in SKILL_CATEGORIES.get(category, []):
                if c_skill.lower() == matched_text:
                    found_canonical = c_skill
                    break
            canonical_name = found_canonical or canonical_name

        if canonical_name not in extracted_skills_map:
            extracted_skills_map[canonical_name] = {
                "category": category,
                "count": 1,
            }
        else:
            extracted_skills_map[canonical_name]["count"] += 1

    # 3. Categorize results into the 7 prompt-required categories
    categorized_skills: Dict[str, List[str]] = {cat: [] for cat in SKILL_CATEGORIES}
    category_counts: Dict[str, int] = {cat: 0 for cat in SKILL_CATEGORIES}
    detected_skills_detail: List[Dict[str, Any]] = []

    for skill_name, data in sorted(extracted_skills_map.items(), key=lambda x: x[0]):
        cat = data["category"]
        if cat in categorized_skills:
            categorized_skills[cat].append(skill_name)
            category_counts[cat] += 1
        else:
            # Fallback category lookup
            inferred_cat = get_category_for_skill(skill_name)
            if inferred_cat in categorized_skills:
                categorized_skills[inferred_cat].append(skill_name)
                category_counts[inferred_cat] += 1
            else:
                categorized_skills.setdefault("Other", []).append(skill_name)

        detected_skills_detail.append(
            {
                "Skill": skill_name,
                "Category": cat,
                "Mentions": data["count"],
            }
        )

    # Sort skills alphabetically within each category
    for cat in categorized_skills:
        categorized_skills[cat].sort()

    total_skills = len(extracted_skills_map)

    # 4. Compute NLP text statistics
    tokens = [token.text for token in doc if not token.is_space and not token.is_punct]
    sentences = list(doc.sents) if doc.has_annotation("SENT_START") else cleaned.split("\n")

    statistics = {
        "word_count": len(tokens),
        "character_count": len(cleaned),
        "sentence_count": max(len(sentences), 1),
        "vocabulary_size": len(set(token.lower() for token in tokens)),
    }

    model_name = getattr(nlp, "meta", {}).get("name", "en_core_web_sm" if "web" in str(nlp) else "spacy.blank('en')")

    return {
        "total_skills": total_skills,
        "category_counts": category_counts,
        "categorized_skills": categorized_skills,
        "detected_skills_detail": detected_skills_detail,
        "cleaned_text": cleaned,
        "statistics": statistics,
        "spacy_model_used": model_name,
    }
