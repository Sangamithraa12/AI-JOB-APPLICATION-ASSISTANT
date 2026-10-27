"""Services package for AI Job Application Assistant."""

from .ai_service import ai_service
from .resume_service import resume_service
from .matching_service import matching_service
from .cover_letter_service import cover_letter_service
from .recruiter_service import recruiter_service
from .interview_service import interview_service
from .prompt_templates import (
    SYSTEM_PROMPT,
    PROMPT_SHOWCASE_CASES,
    JOB_ANALYSIS_USER_PROMPT_TEMPLATE,
    RESUME_MATCHING_USER_PROMPT_TEMPLATE,
    COVER_LETTER_USER_PROMPT_TEMPLATE,
    RECRUITER_MESSAGE_USER_PROMPT_TEMPLATE,
    INTERVIEW_PREP_USER_PROMPT_TEMPLATE,
    INTERVIEW_EVALUATION_USER_PROMPT_TEMPLATE
)

__all__ = [
    "ai_service",
    "resume_service",
    "matching_service",
    "cover_letter_service",
    "recruiter_service",
    "interview_service",
    "SYSTEM_PROMPT",
    "PROMPT_SHOWCASE_CASES",
    "JOB_ANALYSIS_USER_PROMPT_TEMPLATE",
    "RESUME_MATCHING_USER_PROMPT_TEMPLATE",
    "COVER_LETTER_USER_PROMPT_TEMPLATE",
    "RECRUITER_MESSAGE_USER_PROMPT_TEMPLATE",
    "INTERVIEW_PREP_USER_PROMPT_TEMPLATE",
    "INTERVIEW_EVALUATION_USER_PROMPT_TEMPLATE"
]
