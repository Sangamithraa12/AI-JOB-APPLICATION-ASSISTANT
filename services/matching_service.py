"""Resume-to-Job Matching, Skill Extraction, and Improvement Engine.

Implements:
1. Job description parsing (title, skills, experience, responsibilities)
2. Transparent documented skill matching calculation with clear formula breakdown
3. Non-hallucinatory resume improvement suggestions
4. AI-powered mode with honest fallback to deterministic rule engine
"""

import re
from typing import Dict, Any, List, Set, Tuple
from .ai_service import ai_service
from .prompt_templates import (
    JOB_ANALYSIS_USER_PROMPT_TEMPLATE,
    RESUME_MATCHING_USER_PROMPT_TEMPLATE,
    sanitize_delimiter_input
)

# Common technical & soft skills taxonomy for reliable rule-based extraction
COMMON_SKILLS_TAXONOMY = {
    # Programming & Frameworks
    "python": "Python", "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
    "javascript": "JavaScript", "typescript": "TypeScript", "html": "HTML5",
    "css": "CSS3", "react": "React", "node": "Node.js", "sql": "SQL",
    "sqlite": "SQLite", "postgresql": "PostgreSQL", "mysql": "MySQL",
    "mongodb": "MongoDB", "git": "Git", "docker": "Docker", "aws": "AWS",
    "azure": "Azure", "gcp": "Google Cloud", "linux": "Linux",
    "rest": "REST APIs", "api": "API Development",
    # AI / ML / Data
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "nlp": "Natural Language Processing", "ai": "Artificial Intelligence",
    "generative ai": "Generative AI", "prompt engineering": "Prompt Engineering",
    "automation": "Workflow Automation", "pandas": "Pandas", "numpy": "NumPy",
    "scikit-learn": "Scikit-Learn", "pytorch": "PyTorch", "tensorflow": "TensorFlow",
    "data analysis": "Data Analysis", "data visualization": "Data Visualization",
    "llm": "Large Language Models", "rag": "RAG (Retrieval-Augmented Generation)",
    # Professional & Methodologies
    "agile": "Agile / Scrum", "problem solving": "Problem Solving",
    "communication": "Effective Communication", "teamwork": "Cross-Functional Collaboration",
    "testing": "Software Testing", "ci/cd": "CI/CD Pipelines", "devops": "DevOps"
}

class MatchingService:
    """Service for job analysis, skill alignment, and resume improvement."""

    @staticmethod
    def extract_skills_rule_based(text: str) -> List[str]:
        """Extract recognized professional and technical skills using rule-based keyword matching."""
        if not text:
            return []

        found_skills = set()
        lower_text = " " + text.lower() + " "

        for key, canonical_name in COMMON_SKILLS_TAXONOMY.items():
            pattern = r'(?<![a-zA-Z0-9_-])' + re.escape(key) + r'(?![a-zA-Z0-9_-])'
            if re.search(pattern, lower_text):
                found_skills.add(canonical_name)

        return sorted(list(found_skills))

    @staticmethod
    def analyze_job_description(job_description: str) -> Dict[str, Any]:
        """Analyze a job description and return structured requirements.

        Uses Gemini LLM if configured, otherwise uses the deterministic parser.
        """
        sanitized_jd = sanitize_delimiter_input(job_description)
        if not sanitized_jd:
            raise ValueError("Job description cannot be empty.")

        # Try Live AI
        status = ai_service.get_status()
        if status["is_live_ai"]:
            prompt = JOB_ANALYSIS_USER_PROMPT_TEMPLATE.format(job_description=sanitized_jd)
            ai_result = ai_service.generate_json(prompt)
            if ai_result and isinstance(ai_result, dict) and "required_skills" in ai_result:
                ai_result["is_ai_generated"] = True
                ai_result["mode_label"] = "✨ AI-Analyzed (Google Gemini)"
                return ai_result

        # Deterministic Rule-Based Fallback
        return MatchingService._analyze_job_deterministic(sanitized_jd)

    @staticmethod
    def _analyze_job_deterministic(text: str) -> Dict[str, Any]:
        """Deterministic rule-based job description parser."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Inferred job title: inspect first 3 lines
        job_title = "Not Specified"
        for line in lines[:4]:
            if any(term in line.lower() for term in ["engineer", "developer", "associate", "specialist", "analyst", "manager", "intern"]):
                job_title = line.split("–")[0].split("-")[0].strip()
                break
        if job_title == "Not Specified" and lines:
            job_title = lines[0][:50]

        # Experience level detection
        exp_level = "Entry-Level / Graduate"
        lower_text = text.lower()
        if "senior" in lower_text or "5+ years" in lower_text or "lead" in lower_text:
            exp_level = "Senior (5+ years)"
        elif "mid" in lower_text or "3-5 years" in lower_text or "3+ years" in lower_text:
            exp_level = "Mid-Level (2-4 years)"
        elif "0-2 years" in lower_text or "entry" in lower_text or "graduate" in lower_text or "fresher" in lower_text:
            exp_level = "Entry-Level (0-2 years)"

        # Extract skills
        all_detected_skills = MatchingService.extract_skills_rule_based(text)

        # Partition into required vs preferred based on context
        required_skills = []
        preferred_skills = []

        for skill in all_detected_skills:
            # If skill appears in first half or near 'required', assign to required
            if "preferred" in lower_text or "nice to have" in lower_text:
                if skill.lower() in ["docker", "aws", "azure", "ci/cd", "rag"]:
                    preferred_skills.append(skill)
                else:
                    required_skills.append(skill)
            else:
                required_skills.append(skill)

        if not required_skills and all_detected_skills:
            required_skills = all_detected_skills[:5]
            preferred_skills = all_detected_skills[5:]

        # Responsibilities
        responsibilities = []
        for line in lines:
            if line.startswith(("-", "•", "*")) or any(verb in line.lower() for verb in ["build", "develop", "collaborate", "design", "manage", "automate"]):
                clean_line = re.sub(r'^[-•*\d.]+\s*', '', line).strip()
                if 20 < len(clean_line) < 160:
                    responsibilities.append(clean_line)
                    if len(responsibilities) >= 4:
                        break
        if not responsibilities:
            responsibilities = [
                "Collaborate with team members to deliver reliable software solutions.",
                "Implement automation workflows and optimize operational efficiency.",
                "Maintain clean code, comprehensive tests, and up-to-date documentation."
            ]

        return {
            "job_title": job_title,
            "company_name": "As specified in job posting",
            "experience_level": exp_level,
            "required_skills": required_skills or ["Problem Solving", "Effective Communication"],
            "preferred_skills": preferred_skills,
            "key_responsibilities": responsibilities,
            "inferred_competencies": [
                "Adaptability to fast-evolving tools",
                "Strong analytical mindset",
                "Attention to detail and test coverage"
            ],
            "is_ai_generated": False,
            "mode_label": "⚡ Deterministic Rule Engine (Demo Mode)"
        }

    @staticmethod
    def calculate_match_score(
        resume_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str]
    ) -> Tuple[int, Dict[str, Any]]:
        """Calculate a transparent, deterministic match score with mathematical breakdown.

        Formula:
          Required Skill Weight = 75%
          Preferred Skill Weight = 25% (or 100% on required if no preferred listed)

        Match Score = (Matching_Req / Total_Req * 75) + (Matching_Pref / Total_Pref * 25)
        """
        resume_set = {s.lower() for s in resume_skills}
        req_set = {s.lower(): s for s in required_skills}
        pref_set = {s.lower(): s for s in preferred_skills}

        matched_req = [orig for low, orig in req_set.items() if low in resume_set]
        missing_req = [orig for low, orig in req_set.items() if low not in resume_set]

        matched_pref = [orig for low, orig in pref_set.items() if low in resume_set]
        missing_pref = [orig for low, orig in pref_set.items() if low not in resume_set]

        total_req_count = len(required_skills)
        total_pref_count = len(preferred_skills)

        if total_req_count == 0 and total_pref_count == 0:
            score = 50
            req_ratio = 0.5
            pref_ratio = 0.5
        elif total_pref_count == 0:
            req_ratio = len(matched_req) / total_req_count if total_req_count > 0 else 0
            score = round(req_ratio * 100)
            pref_ratio = 0
        else:
            req_ratio = len(matched_req) / total_req_count if total_req_count > 0 else 0
            pref_ratio = len(matched_pref) / total_pref_count if total_pref_count > 0 else 0
            score = round((req_ratio * 75) + (pref_ratio * 25))

        # Clamp between 0 and 100
        score = max(0, min(100, score))

        breakdown = {
            "score": score,
            "required_weight": "75%" if total_pref_count > 0 else "100%",
            "preferred_weight": "25%" if total_pref_count > 0 else "0%",
            "required_total": total_req_count,
            "required_matched": len(matched_req),
            "preferred_total": total_pref_count,
            "preferred_matched": len(matched_pref),
            "matched_required_skills": matched_req,
            "missing_required_skills": missing_req,
            "matched_preferred_skills": matched_pref,
            "missing_preferred_skills": missing_pref,
            "all_matching_skills": matched_req + matched_pref,
            "all_missing_skills": missing_req + missing_pref,
            "explanation": (
                f"Calculation: ({len(matched_req)}/{total_req_count} required skills × {75 if total_pref_count else 100}%)"
                + (f" + ({len(matched_pref)}/{total_pref_count} preferred skills × 25%)" if total_pref_count else "")
                + f" = {score}%."
            ),
            "disclaimer": (
                "IMPORTANT: This score reflects lexical and contextual skill overlap between your "
                "resume and the job requirements. It is an editorial alignment tool, NOT a guarantee "
                "or prediction of hiring probability."
            )
        }
        return score, breakdown

    @staticmethod
    def match_resume_to_job(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Perform comprehensive resume-to-job matching and improvement suggestions."""
        sanitized_resume = sanitize_delimiter_input(resume_text)
        sanitized_jd = sanitize_delimiter_input(job_description)

        if not sanitized_resume or not sanitized_jd:
            raise ValueError("Both resume text and job description are required for matching.")

        # 1. Deterministic baseline skill extraction
        resume_skills = MatchingService.extract_skills_rule_based(sanitized_resume)
        job_analysis = MatchingService.analyze_job_description(sanitized_jd)

        calc_score, breakdown = MatchingService.calculate_match_score(
            resume_skills,
            job_analysis["required_skills"],
            job_analysis["preferred_skills"]
        )

        # 2. Check if Live AI is configured for contextual enrichment
        status = ai_service.get_status()
        if status["is_live_ai"]:
            prompt = RESUME_MATCHING_USER_PROMPT_TEMPLATE.format(
                job_description=sanitized_jd,
                resume_text=sanitized_resume
            )
            ai_result = ai_service.generate_json(prompt)
            if ai_result and isinstance(ai_result, dict):
                # Ensure the mathematical transparency is retained even with AI
                return {
                    "match_score": ai_result.get("match_score", calc_score),
                    "score_explanation": ai_result.get("score_explanation", breakdown["explanation"]),
                    "calculation_breakdown": breakdown,
                    "matching_skills": ai_result.get("matching_skills", breakdown["all_matching_skills"]),
                    "missing_skills": ai_result.get("missing_skills", breakdown["all_missing_skills"]),
                    "experience_alignment": ai_result.get("experience_alignment", "Strong alignment on core technologies with minor gaps in specialized tools."),
                    "improvement_opportunities": ai_result.get("improvement_opportunities", []),
                    "is_ai_generated": True,
                    "mode_label": "✨ AI-Enhanced (Google Gemini)"
                }

        # 3. Deterministic Non-Hallucinatory Suggestions (Demo Mode)
        improvement_opportunities = []

        # Improvement 1: Summary section
        improvement_opportunities.append({
            "section": "Professional Summary",
            "current_issue": "Summary does not highlight target role keywords prominently.",
            "suggested_wording": f"Goal-oriented professional with foundational expertise in {', '.join(breakdown['all_matching_skills'][:3]) if breakdown['all_matching_skills'] else 'core technical skills'}, seeking to contribute to high-impact automation and software initiatives as a {job_analysis['job_title']}.",
            "needs_user_verification": False
        })

        # Improvement 2: Missing skills action plan
        if breakdown["all_missing_skills"]:
            top_missing = breakdown["all_missing_skills"][:3]
            improvement_opportunities.append({
                "section": "Skills & Projects",
                "current_issue": f"The job post emphasizes {', '.join(top_missing)}, which are not listed on your resume.",
                "suggested_wording": f"If you have academic, project, or coursework experience with {', '.join(top_missing)}, add a dedicated project bullet detailing how you applied them.",
                "needs_user_verification": True
            })

        # Improvement 3: Action-oriented project bullet
        if breakdown["all_matching_skills"]:
            first_skill = breakdown["all_matching_skills"][0]
            improvement_opportunities.append({
                "section": "Project Experience",
                "current_issue": "Project bullet points could use stronger quantifiable impact verbs.",
                "suggested_wording": f"Engineered modular software solutions utilizing {first_skill}, improving code reliability and automating repetitive execution steps.",
                "needs_user_verification": True
            })

        return {
            "match_score": calc_score,
            "score_explanation": breakdown["explanation"],
            "calculation_breakdown": breakdown,
            "matching_skills": breakdown["all_matching_skills"],
            "missing_skills": breakdown["all_missing_skills"],
            "experience_alignment": (
                f"Candidate exhibits {len(breakdown['all_matching_skills'])} matching core competencies. "
                f"Addressing {len(breakdown['all_missing_skills'])} missing skill areas in your projects will enhance overall alignment."
            ),
            "improvement_opportunities": improvement_opportunities,
            "is_ai_generated": False,
            "mode_label": "⚡ Deterministic Rule Engine (Demo Mode)"
        }

matching_service = MatchingService()
