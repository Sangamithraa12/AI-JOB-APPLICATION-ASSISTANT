"""Recruiter message generator service supporting multiple outreach scenarios and tones."""

from typing import Dict, Any, Optional
from .ai_service import ai_service
from .matching_service import matching_service
from .prompt_templates import (
    RECRUITER_MESSAGE_USER_PROMPT_TEMPLATE,
    sanitize_delimiter_input
)

MESSAGE_TYPES = [
    "Application Follow-up",
    "Cold Outreach / Inquiring About Openings",
    "Employee Referral Request",
    "Recruiter Outreach / InMail",
    "Interview Availability & Rescheduling"
]

MESSAGE_TONES = [
    "Professional & Polite",
    "Warm & Approachable",
    "Direct & Concise"
]

class RecruiterService:
    """Generates concise, polite messages for networking and recruiter communication."""

    @staticmethod
    def generate_message(
        message_type: str,
        company_name: str,
        job_title: str,
        tone: str = "Professional & Polite",
        resume_text: str = "",
        recipient_name: str = "",
        additional_notes: str = ""
    ) -> Dict[str, Any]:
        """Generate a focused networking or recruiter message."""
        company = company_name.strip() if company_name else "[Company Name]"
        role = job_title.strip() if job_title else "[Target Role]"
        recipient = recipient_name.strip() if recipient_name else "Hiring Team"

        if message_type not in MESSAGE_TYPES:
            message_type = "Application Follow-up"

        sanitized_resume = sanitize_delimiter_input(resume_text)

        # Check Live AI
        status = ai_service.get_status()
        if status["is_live_ai"]:
            prompt = RECRUITER_MESSAGE_USER_PROMPT_TEMPLATE.format(
                message_type=message_type,
                tone=tone,
                company_name=company,
                job_title=role,
                additional_context=f"Recipient: {recipient}. Notes: {additional_notes}",
                resume_text=sanitized_resume
            )
            ai_text = ai_service.generate_text(prompt)
            if ai_text and len(ai_text.strip()) > 30:
                return {
                    "subject": RecruiterService._extract_or_generate_subject(ai_text, message_type, role, company),
                    "message_body": ai_text.strip(),
                    "message_type": message_type,
                    "tone": tone,
                    "is_ai_generated": True,
                    "mode_label": "✨ AI-Generated (Google Gemini)"
                }

        # Deterministic Grounded Templates (Demo Mode)
        return RecruiterService._generate_deterministic_message(
            message_type, company, role, recipient, tone, sanitized_resume, additional_notes
        )

    @staticmethod
    def _extract_or_generate_subject(text: str, msg_type: str, role: str, company: str) -> str:
        """Extract subject line if present in text, else provide standard subject."""
        lines = text.splitlines()
        for line in lines[:3]:
            if line.lower().startswith("subject:"):
                return line.split(":", 1)[1].strip()

        defaults = {
            "Application Follow-up": f"Following Up: Application for {role} - [Your Name]",
            "Cold Outreach / Inquiring About Openings": f"Inquiry regarding {role} opportunities at {company}",
            "Employee Referral Request": f"Connecting regarding {role} opening at {company}",
            "Recruiter Outreach / InMail": f"Candidate Profile: {role} opportunities at {company}",
            "Interview Availability & Rescheduling": f"Update regarding interview for {role} - [Your Name]"
        }
        return defaults.get(msg_type, f"Inquiry regarding {role} at {company}")

    @staticmethod
    def _generate_deterministic_message(
        msg_type: str,
        company: str,
        role: str,
        recipient: str,
        tone: str,
        resume_text: str,
        notes: str
    ) -> Dict[str, Any]:
        """Generate deterministic outreach messages based on message type."""
        skills = matching_service.extract_skills_rule_based(resume_text)
        top_skills = ", ".join(skills[:3]) if skills else "software development and problem-solving"

        templates = {
            "Application Follow-up": (
                f"Subject: Following Up: Application for {role} - [Your Name]\n\n"
                f"Hi {recipient},\n\n"
                f"I hope you're having a productive week! I recently submitted my application for the {role} position at {company}. "
                f"With practical experience in {top_skills}, I am very excited about the opportunity to contribute to your team's initiatives.\n\n"
                f"I wanted to briefly reiterate my strong enthusiasm for this role and confirm if any additional details or portfolio links would be helpful at this stage.\n\n"
                f"Thank you for your time and consideration!\n\n"
                f"Best regards,\n"
                f"[Your Name]\n"
                f"[LinkedIn Profile / Portfolio]"
            ),
            "Cold Outreach / Inquiring About Openings": (
                f"Subject: Inquiry regarding early-career {role} opportunities at {company}\n\n"
                f"Hi {recipient},\n\n"
                f"I've been closely following {company}'s impressive growth and work in technology automation. "
                f"As a prospective {role} with hands-on skills in {top_skills}, I am eager to learn if your team is exploring new talent additions for junior or associate positions.\n\n"
                f"If you have 5-10 minutes in the coming weeks, I would love the chance to connect and ask a couple of quick questions about your team's engineering priorities.\n\n"
                f"Thank you for your time!\n\n"
                f"Warm regards,\n"
                f"[Your Name]"
            ),
            "Employee Referral Request": (
                f"Subject: Quick question regarding the {role} opening at {company}\n\n"
                f"Hi {recipient},\n\n"
                f"I came across your profile and noticed your impactful work on the engineering team at {company}. "
                f"I noticed an open {role} position and believe my background in {top_skills} aligns well with the team's needs.\n\n"
                f"Would you be open to a quick 5-minute chat about your experience at {company}? If you feel my profile is a good match, I would be deeply grateful for an employee referral.\n\n"
                f"Thank you so much for your guidance!\n\n"
                f"Best regards,\n"
                f"[Your Name]"
            ),
            "Recruiter Outreach / InMail": (
                f"Subject: Passionate {role} Candidate - [Your Name]\n\n"
                f"Hi {recipient},\n\n"
                f"I hope you're doing well! I am reaching out to introduce myself as a candidate interested in {role} openings at {company}.\n\n"
                f"My background centers on building maintainable software with {top_skills}. I pride myself on rapid learning, proactive communication, and high attention to test quality.\n\n"
                f"I would welcome the opportunity to share my resume and discuss how I can support upcoming projects at {company}.\n\n"
                f"Sincerely,\n"
                f"[Your Name]"
            ),
            "Interview Availability & Rescheduling": (
                f"Subject: Interview Availability Update: {role} - [Your Name]\n\n"
                f"Dear {recipient},\n\n"
                f"Thank you very much for coordinating the interview process for the {role} opening at {company}. "
                f"I am writing to update my availability for our upcoming conversation.\n\n"
                f"{notes if notes else 'I am fully available for 30-45 minute slots during the following windows: [Insert Date/Times].'}\n\n"
                f"Please let me know which time works best for the team. I look forward to our discussion!\n\n"
                f"Best regards,\n"
                f"[Your Name]"
            )
        }

        body = templates.get(msg_type, templates["Application Follow-up"])
        subject = RecruiterService._extract_or_generate_subject(body, msg_type, role, company)

        return {
            "subject": subject,
            "message_body": body,
            "message_type": msg_type,
            "tone": tone,
            "is_ai_generated": False,
            "mode_label": "⚡ Deterministic Grounded Engine (Demo Mode)"
        }

recruiter_service = RecruiterService()
