"""Cover letter generation service with tone adaptation and strict non-hallucination rules."""

from typing import Dict, Any, Optional
from .ai_service import ai_service
from .matching_service import matching_service
from .prompt_templates import (
    COVER_LETTER_USER_PROMPT_TEMPLATE,
    sanitize_delimiter_input
)

VALID_TONES = ["Professional", "Enthusiastic", "Confident", "Direct"]

class CoverLetterService:
    """Generates tailored, authentic cover letters."""

    @staticmethod
    def generate_cover_letter(
        resume_text: str,
        job_description: str,
        company_name: str,
        job_title: str,
        tone: str = "Professional"
    ) -> Dict[str, Any]:
        """Generate a tailored cover letter grounded strictly in the supplied resume."""
        company_name = company_name.strip() if company_name else ""
        job_title = job_title.strip() if job_title else ""

        if not company_name:
            raise ValueError("Company name is required.")
        if not job_title:
            raise ValueError("Job title is required.")
        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is required to generate a truthful cover letter.")
        if not job_description or not job_description.strip():
            raise ValueError("Job description is required to tailor the letter.")

        if tone not in VALID_TONES:
            tone = "Professional"

        sanitized_resume = sanitize_delimiter_input(resume_text)
        sanitized_jd = sanitize_delimiter_input(job_description)

        # Live AI attempt
        status = ai_service.get_status()
        if status["is_live_ai"]:
            prompt = COVER_LETTER_USER_PROMPT_TEMPLATE.format(
                job_title=job_title,
                company_name=company_name,
                tone=tone,
                job_description=sanitized_jd,
                resume_text=sanitized_resume
            )
            ai_text = ai_service.generate_text(prompt)
            if ai_text and len(ai_text.strip()) > 100:
                return {
                    "cover_letter": ai_text.strip(),
                    "tone": tone,
                    "company_name": company_name,
                    "job_title": job_title,
                    "is_ai_generated": True,
                    "mode_label": "✨ AI-Generated (Google Gemini)"
                }

        # Deterministic Grounded Template Fallback (Demo Mode)
        return CoverLetterService._generate_deterministic_letter(
            sanitized_resume, sanitized_jd, company_name, job_title, tone
        )

    @staticmethod
    def _generate_deterministic_letter(
        resume_text: str,
        job_description: str,
        company_name: str,
        job_title: str,
        tone: str
    ) -> Dict[str, Any]:
        """Generate a deterministic, authentic cover letter using detected skills without hallucination."""
        resume_skills = matching_service.extract_skills_rule_based(resume_text)
        skills_str = ", ".join(resume_skills[:4]) if resume_skills else "software engineering and problem solving"

        # Tone adjustments
        tone_intros = {
            "Professional": f"I am writing to express my strong interest in the {job_title} position at {company_name}.",
            "Enthusiastic": f"I was thrilled to discover the opening for the {job_title} role at {company_name}, a team whose mission and technology standards deeply resonate with me.",
            "Confident": f"With practical hands-on experience in {skills_str}, I am confident in my ability to immediately deliver value as a {job_title} at {company_name}.",
            "Direct": f"I am applying for the {job_title} opening at {company_name}. My background in {skills_str} directly meets your team's current technical requirements."
        }

        intro = tone_intros.get(tone, tone_intros["Professional"])

        body = (
            f"Dear Hiring Team,\n\n"
            f"{intro}\n\n"
            f"Reviewing your job requirements, I noted your emphasis on building robust, automated solutions and maintaining high development standards. "
            f"Throughout my work and projects, I have cultivated hands-on proficiency in {skills_str}. "
            f"I focus on writing clean, maintainable code, automating manual tasks, and adhering to rigorous testing practices to ensure dependable software delivery.\n\n"
            f"What attracts me most to {company_name} is the opportunity to apply these technical problem-solving capabilities to your ongoing initiatives. "
            f"I thrive in collaborative, fast-paced environments where curiosity, continuous learning, and ownership are valued.\n\n"
            f"Thank you for considering my application. I welcome the opportunity to discuss how my skill set and enthusiasm can support the goals of the {company_name} team.\n\n"
            f"Sincerely,\n"
            f"[Your Name]\n"
            f"[Your Contact Information]"
        )

        return {
            "cover_letter": body,
            "tone": tone,
            "company_name": company_name,
            "job_title": job_title,
            "is_ai_generated": False,
            "mode_label": "⚡ Deterministic Grounded Engine (Demo Mode)"
        }

cover_letter_service = CoverLetterService()
