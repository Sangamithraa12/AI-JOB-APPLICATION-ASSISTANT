"""Interview preparation service with grounded answers and candidate practice mode feedback."""

from typing import Dict, Any, List, Optional
from .ai_service import ai_service
from .matching_service import matching_service
from .prompt_templates import (
    INTERVIEW_PREP_USER_PROMPT_TEMPLATE,
    INTERVIEW_EVALUATION_USER_PROMPT_TEMPLATE,
    sanitize_delimiter_input
)

class InterviewService:
    """Manages role-tailored question generation and candidate answer evaluation."""

    @staticmethod
    def generate_interview_questions(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Generate structured Technical, HR, and Project interview questions grounded in inputs."""
        sanitized_resume = sanitize_delimiter_input(resume_text)
        sanitized_jd = sanitize_delimiter_input(job_description)

        if not sanitized_jd:
            raise ValueError("Job description is required to generate interview questions.")

        # Live AI attempt
        status = ai_service.get_status()
        if status["is_live_ai"]:
            prompt = INTERVIEW_PREP_USER_PROMPT_TEMPLATE.format(
                job_description=sanitized_jd,
                resume_text=sanitized_resume or "No specific resume supplied. Tailor questions to job description."
            )
            ai_result = ai_service.generate_json(prompt)
            if ai_result and isinstance(ai_result, dict) and "questions" in ai_result:
                return {
                    "questions": ai_result["questions"],
                    "is_ai_generated": True,
                    "mode_label": "✨ AI-Generated (Google Gemini)"
                }

        # Deterministic Grounded Preparation (Demo Mode)
        return InterviewService._generate_deterministic_questions(sanitized_resume, sanitized_jd)

    @staticmethod
    def evaluate_practice_answer(
        job_title: str,
        question: str,
        candidate_answer: str
    ) -> Dict[str, Any]:
        """Evaluate a candidate's answer submitted in practice mode."""
        role = job_title.strip() if job_title else "Software Associate"
        q_text = question.strip() if question else "General Interview Question"
        c_answer = sanitize_delimiter_input(candidate_answer)

        if not c_answer or len(c_answer) < 15:
            raise ValueError("Please provide a more detailed practice answer (at least 15 characters).")

        # Live AI attempt
        status = ai_service.get_status()
        if status["is_live_ai"]:
            prompt = INTERVIEW_EVALUATION_USER_PROMPT_TEMPLATE.format(
                job_title=role,
                question=q_text,
                candidate_answer=c_answer
            )
            ai_result = ai_service.generate_json(prompt)
            if ai_result and isinstance(ai_result, dict) and "strengths" in ai_result:
                ai_result["is_ai_generated"] = True
                ai_result["mode_label"] = "✨ AI-Evaluated (Google Gemini)"
                return ai_result

        # Deterministic Practice Feedback (Demo Mode)
        word_count = len(c_answer.split())
        has_star_hints = any(w in c_answer.lower() for w in ["situation", "task", "action", "result", "when", "first", "then", "solved", "implemented"])
        has_metrics = any(char.isdigit() for char in c_answer)

        strengths = []
        improvements = []
        score = 65

        if word_count >= 50:
            strengths.append("Thorough response length with good contextual detail.")
            score += 15
        else:
            improvements.append("Response is somewhat brief. Elaborate further on the specific steps you personally took.")

        if has_star_hints:
            strengths.append("Logical sequencing showing clear action and resolution.")
            score += 10
        else:
            improvements.append("Incorporate the STAR framework (Situation, Task, Action, Result) to make your delivery crisper.")

        if has_metrics:
            strengths.append("Included quantitative references or tangible results.")
            score += 10
        else:
            improvements.append("Add measurable outcomes or metrics (e.g., '% time saved', 'number of test cases', or 'latency decrease').")

        rating = "Strong" if score >= 85 else ("Satisfactory" if score >= 70 else "Needs Improvement")

        return {
            "overall_rating": rating,
            "score": min(score, 95),
            "strengths": strengths or ["Directly addressed the question topic.", "Good professional vocabulary."],
            "areas_for_improvement": improvements or ["Consider closing with a forward-looking summary of lessons learned."],
            "improved_model_answer": (
                f"In my previous work, I encountered a situation directly relevant to this: {c_answer} "
                f"To maximize the impact, I ensured all stakeholders were updated, validated the solution with automated tests, "
                f"and documented the findings for future maintainability."
            ),
            "is_ai_generated": False,
            "mode_label": "⚡ Deterministic Evaluation Engine (Demo Mode)"
        }

    @staticmethod
    def _generate_deterministic_questions(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Generate 6 realistic deterministic interview questions grounded in inputs."""
        skills = matching_service.extract_skills_rule_based(resume_text or job_description)
        tech_1 = skills[0] if skills else "Python"
        tech_2 = skills[1] if len(skills) > 1 else "REST APIs"

        questions = [
            {
                "id": 1,
                "category": "Technical",
                "question": f"How do you design, test, and debug an application component using {tech_1}?",
                "suggested_answer": (
                    f"Situation: While building an application module using {tech_1}, I needed to ensure high reliability and modularity.\n"
                    f"Task: My goal was to create clean functions with isolated unit tests and robust error handling.\n"
                    f"Action: I implemented structured typing, wrapped edge cases in custom exceptions, and wrote automated test fixtures.\n"
                    f"Result: Delivered a maintainable service that passed all test suites and facilitated seamless integration."
                ),
                "follow_up_questions": [
                    f"What common bottlenecks or memory issues have you encountered in {tech_1}?",
                    "How do you approach automated testing for backend endpoints?"
                ],
                "key_points_to_emphasize": [
                    "Clean code and defensive programming",
                    "Automated testing and edge case coverage"
                ]
            },
            {
                "id": 2,
                "category": "Technical",
                "question": f"Explain your workflow when consuming or implementing {tech_2} in a production-ready application.",
                "suggested_answer": (
                    f"Situation: Modern software systems rely heavily on robust data exchange through {tech_2}.\n"
                    f"Task: I was responsible for structuring API payloads with predictable status codes and consistent validation.\n"
                    f"Action: I utilized JSON schemas, enforced parameter sanitization, and handled network timeouts gracefully.\n"
                    f"Result: Eliminated unhandled 500 errors and provided transparent API documentation."
                ),
                "follow_up_questions": [
                    "How do you handle API rate limits and token authentication?",
                    "What strategies do you use for backward compatibility?"
                ],
                "key_points_to_emphasize": [
                    "HTTP status code best practices",
                    "Graceful error handling and timeouts"
                ]
            },
            {
                "id": 3,
                "category": "Project & Experience",
                "question": "Walk me through one of the technical projects listed on your resume. What was your specific contribution?",
                "suggested_answer": (
                    "Situation: In my featured technical project, our objective was to solve a specific workflow automation challenge.\n"
                    "Task: I was tasked with designing the backend logic and integrating data persistence.\n"
                    "Action: I authored modular Python code, structured the database tables, and conducted peer code reviews.\n"
                    "Result: Successfully launched the working project on schedule with full documentation."
                ),
                "follow_up_questions": [
                    "If you had another month to work on that project, what architectural change would you make?",
                    "How did you validate your solution with real users?"
                ],
                "key_points_to_emphasize": [
                    "Your personal hands-on contributions",
                    "Practical problem-solving under constraints"
                ]
            },
            {
                "id": 4,
                "category": "Project & Experience",
                "question": "Describe a challenging bug or performance bottleneck you encountered in a recent project and how you resolved it.",
                "suggested_answer": (
                    "Situation: During integration testing, an endpoint exhibited unexpected latency and sporadic failures.\n"
                    "Task: I needed to diagnose whether the root cause was in database queries or external API timeouts.\n"
                    "Action: I profiled the execution path using logging timestamps, identified redundant SQL queries, and added indexing.\n"
                    "Result: Query execution time dropped significantly, and error rates returned to zero."
                ),
                "follow_up_questions": [
                    "How do you prevent similar regressions from reaching production?",
                    "What monitoring tools do you prefer for local debugging?"
                ],
                "key_points_to_emphasize": [
                    "Methodical diagnostic approach rather than guessing",
                    "Measuring before and after performance"
                ]
            },
            {
                "id": 5,
                "category": "HR & Behavioral",
                "question": "Tell me about a time you had to learn a completely new tool or framework under a tight deadline.",
                "suggested_answer": (
                    "Situation: I had to adopt a new library and workflow for an upcoming project requirement with limited prior exposure.\n"
                    "Task: I needed to become productive within three days to avoid delaying the sprint milestone.\n"
                    "Action: I read the official quickstart documentation, built a small proof-of-concept prototype, and consulted community examples.\n"
                    "Result: Successfully implemented the required feature on time with clean code."
                ),
                "follow_up_questions": [
                    "How do you evaluate whether a new library is stable enough for production?",
                    "Who do you reach out to when you are blocked?"
                ],
                "key_points_to_emphasize": [
                    "Fast learning agility and curiosity",
                    "Resourcefulness and self-direction"
                ]
            },
            {
                "id": 6,
                "category": "HR & Behavioral",
                "question": "Why are you interested in this specific role, and how does your background align with our team's mission?",
                "suggested_answer": (
                    "Situation: I have followed this team's work in building high-quality automation and scalable systems.\n"
                    "Task: I sought an opportunity where my foundational programming skills and enthusiasm for AI automation could create real business value.\n"
                    "Action: I analyzed your job posting, identified direct overlap with my technical skill set, and prepared tailored project demonstrations.\n"
                    "Result: I am ready to ramp up swiftly and contribute with diligence and collaborative teamwork from day one."
                ),
                "follow_up_questions": [
                    "Where do you see your technical growth progressing over the next two years?",
                    "What type of engineering culture brings out your best work?"
                ],
                "key_points_to_emphasize": [
                    "Genuine enthusiasm for the company and domain",
                    "Commitment to high quality and continuous improvement"
                ]
            }
        ]

        return {
            "questions": questions,
            "is_ai_generated": False,
            "mode_label": "⚡ Deterministic Grounded Engine (Demo Mode)"
        }

interview_service = InterviewService()
