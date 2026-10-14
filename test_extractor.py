"""
test_extractor.py
Automated end-to-end verification script for Resume Skill Extractor.
Tests parser, NLP pipeline, skill dictionary, and categorization.
"""

import os
import sys
import unittest

import skills
import resume_parser
import nlp_processor

class TestSkillsDictionary(unittest.TestCase):
    def test_categories_presence(self):
        cats = skills.get_skill_categories()
        required_cats = [
            "Programming Languages",
            "Web Development",
            "Databases",
            "AI/ML",
            "Data Science",
            "Tools/Platforms",
            "Cloud/DevOps"
        ]
        for rc in required_cats:
            self.assertIn(rc, cats, f"Required category '{rc}' missing from SKILL_CATEGORIES")
            self.assertGreater(len(cats[rc]), 0, f"Category '{rc}' has no skills")

    def test_alias_lookup(self):
        self.assertEqual(skills.get_category_for_skill("python"), "Programming Languages")
        self.assertEqual(skills.get_category_for_skill("react.js"), "Web Development")
        self.assertEqual(skills.get_category_for_skill("postgres"), "Databases")
        self.assertEqual(skills.get_category_for_skill("pytorch"), "AI/ML")
        self.assertEqual(skills.get_category_for_skill("pandas"), "Data Science")
        self.assertEqual(skills.get_category_for_skill("docker"), "Cloud/DevOps")
        self.assertEqual(skills.get_category_for_skill("git"), "Tools/Platforms")


class TestResumeParser(unittest.TestCase):
    def test_docx_parsing(self):
        docx_path = os.path.join("sample_resumes", "sample_software_engineer_resume.docx")
        text, err = resume_parser.parse_resume(docx_path)
        self.assertIsNone(err, f"DOCX parsing produced error: {err}")
        self.assertIn("Alex Mercer", text)
        self.assertIn("Python", text)
        self.assertIn("React", text)

    def test_pdf_parsing(self):
        pdf_path = os.path.join("sample_resumes", "sample_ai_engineer_resume.pdf")
        text, err = resume_parser.parse_resume(pdf_path)
        self.assertIsNone(err, f"PDF parsing produced error: {err}")
        self.assertIn("Sarah Jenkins", text)
        self.assertIn("PyTorch", text)
        self.assertIn("Data Science", text)

    def test_empty_file_or_invalid_extension(self):
        # Invalid extension
        text, err = resume_parser.parse_resume("invalid_resume.xyz")
        self.assertIsNotNone(err)
        self.assertIn("Unsupported file type", err)

        # None file
        text, err = resume_parser.parse_resume(None)
        self.assertIsNotNone(err)


class TestNLPProcessor(unittest.TestCase):
    def test_clean_text(self):
        raw = "John Doe\nEmail: test@example.com Phone: (555) 123-4567\n• Skill: Python and C++"
        cleaned = nlp_processor.clean_text(raw)
        self.assertNotIn("test@example.com", cleaned)
        self.assertNotIn("(555) 123-4567", cleaned)
        self.assertIn("Python", cleaned)
        self.assertIn("C++", cleaned)

    def test_skills_extraction_software_engineer(self):
        text = """
        Experienced Full-Stack Developer proficient in Python, TypeScript, and Java.
        Strong experience building frontend interfaces in React.js, Next.js, and Tailwind CSS.
        Database expertise in PostgreSQL, Redis, and MongoDB.
        Cloud & DevOps skills include Docker, Kubernetes, AWS, and CI/CD pipelines.
        Tools: Git, VS Code, Linux.
        """
        result = nlp_processor.extract_skills_from_text(text)
        self.assertGreater(result["total_skills"], 10)
        
        cats = result["categorized_skills"]
        self.assertIn("Python", cats["Programming Languages"])
        self.assertIn("React.js", cats["Web Development"])
        self.assertIn("PostgreSQL", cats["Databases"])
        self.assertIn("Docker", cats["Cloud/DevOps"])
        self.assertIn("Git", cats["Tools/Platforms"])

    def test_special_symbols(self):
        text = "Proficient in C++, C#, .NET, CI/CD, Node.js, and Scikit-learn."
        result = nlp_processor.extract_skills_from_text(text)
        detected = [d["Skill"] for d in result["detected_skills_detail"]]
        self.assertIn("C++", detected)
        self.assertIn("C#", detected)
        self.assertIn("CI/CD", detected)
        self.assertIn("Node.js", detected)
        self.assertIn("Scikit-learn", detected)

    def test_empty_text(self):
        result = nlp_processor.extract_skills_from_text("")
        self.assertEqual(result["total_skills"], 0)
        self.assertEqual(len(result["detected_skills_detail"]), 0)

    def test_non_technical_text(self):
        text = "Grocery list: milk, eggs, bread, butter, fresh apples, and laundry detergent."
        result = nlp_processor.extract_skills_from_text(text)
        self.assertEqual(result["total_skills"], 0)


if __name__ == "__main__":
    unittest.main()
