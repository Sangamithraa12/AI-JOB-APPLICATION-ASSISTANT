"""AI Job Application Assistant - Main Flask Application.

Built for the Gokul Infocare AI Growth & Automation Associate practical assessment.
Full-stack implementation featuring PDF parsing, job analysis, transparent skill matching,
grounded cover letters, recruiter messaging, interview preparation, SQLite application tracking,
and prompt engineering showcase.
"""

import os
import tempfile
from pathlib import Path
from flask import (
    Flask, render_template, request, jsonify, send_file, redirect, url_for
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from database import (
    init_db,
    add_application,
    get_applications,
    get_application_by_id,
    update_application,
    delete_application,
    get_application_stats,
    VALID_STATUSES
)
from services import (
    ai_service,
    resume_service,
    matching_service,
    cover_letter_service,
    recruiter_service,
    interview_service,
    SYSTEM_PROMPT,
    PROMPT_SHOWCASE_CASES,
    JOB_ANALYSIS_USER_PROMPT_TEMPLATE,
    RESUME_MATCHING_USER_PROMPT_TEMPLATE,
    COVER_LETTER_USER_PROMPT_TEMPLATE,
    RECRUITER_MESSAGE_USER_PROMPT_TEMPLATE,
    INTERVIEW_PREP_USER_PROMPT_TEMPLATE,
    INTERVIEW_EVALUATION_USER_PROMPT_TEMPLATE
)

app = Flask(__name__)
app.config.from_object(Config)

# Ensure uploads directory exists
Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Initialize database schema and initial demonstration seed data
with app.app_context():
    init_db(seed_sample_data=True)

# ---------------------------------------------------------------------------
# Global Context Processor
# ---------------------------------------------------------------------------
@app.context_processor
def inject_global_data():
    """Inject AI status and active route info into all Jinja templates."""
    return {
        "ai_status": ai_service.get_status(),
        "valid_statuses": VALID_STATUSES
    }

# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404
    return render_template("base.html", page_title="Page Not Found", error_message="The requested page does not exist."), 404

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    return jsonify({
        "success": False,
        "error": f"File is too large. Maximum permitted size is {Config.MAX_CONTENT_LENGTH // (1024 * 1024)}MB."
    }), 413

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    app.logger.error("Unhandled error: %s", error)
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": str(error)}), 500
    return render_template("base.html", page_title="Error", error_message="An internal server error occurred."), 500

# ---------------------------------------------------------------------------
# Frontend Page Routes (HTML Views)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Dashboard view displaying live application metrics and quick links."""
    stats = get_application_stats()
    return render_template("index.html", stats=stats, active_page="dashboard")

@app.route("/resume-analyzer")
def resume_analyzer_page():
    """Resume upload, validation, and text extraction view."""
    return render_template("resume_analyzer.html", active_page="resume_analyzer")

@app.route("/job-analyzer")
def job_analyzer_page():
    """Job description analysis view."""
    return render_template("job_analyzer.html", active_page="job_analyzer")

@app.route("/matching")
def matching_page():
    """Resume-to-Job matching and improvement suggestion view."""
    return render_template("matching.html", active_page="matching")

@app.route("/cover-letter")
def cover_letter_page():
    """Customized cover letter generator view."""
    return render_template("cover_letter.html", active_page="cover_letter")

@app.route("/recruiter-messages")
def recruiter_messages_page():
    """Concise recruiter and networking message generator view."""
    return render_template("recruiter_messages.html", active_page="recruiter_messages")

@app.route("/interview-prep")
def interview_prep_page():
    """Interview preparation and practice sandbox view."""
    return render_template("interview_prep.html", active_page="interview_prep")

@app.route("/tracker")
def tracker_page():
    """SQLite-backed application tracker view."""
    stats = get_application_stats()
    return render_template("tracker.html", stats=stats, active_page="tracker")

@app.route("/prompt-showcase")
def prompt_showcase_page():
    """AI Prompt Engineering Showcase and live production inspector view."""
    return render_template(
        "prompt_showcase.html",
        showcase_cases=PROMPT_SHOWCASE_CASES,
        system_prompt=SYSTEM_PROMPT,
        active_page="prompt_showcase"
    )

@app.route("/about")
def about_page():
    """About project, assessment context, architecture, and privacy notice."""
    return render_template("about.html", active_page="about")

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.route("/api/status", methods=["GET"])
def api_status():
    """Check AI provider configuration status."""
    return jsonify({
        "success": True,
        "status": ai_service.get_status()
    })

@app.route("/api/dashboard/stats", methods=["GET"])
def api_dashboard_stats():
    """Retrieve real-time application metrics from SQLite."""
    try:
        stats = get_application_stats()
        return jsonify({"success": True, "stats": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/resume/upload", methods=["POST"])
def api_resume_upload():
    """Validate and extract text from an uploaded PDF resume."""
    if "resume" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded. Please select a PDF file."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    if not resume_service.allowed_file(file.filename):
        return jsonify({"success": False, "error": "Invalid file format. Only PDF (.pdf) documents are accepted."}), 400

    temp_path = None
    try:
        # Save securely to temporary location for pypdf stream reading
        safe_name = secure_filename(file.filename)
        temp_fd, temp_path_str = tempfile.mkstemp(suffix=".pdf", prefix="upload_")
        os.close(temp_fd)
        temp_path = Path(temp_path_str)
        file.save(str(temp_path))

        # Extract text and validate
        extracted_text, metadata = resume_service.extract_text_from_pdf_stream(str(temp_path))

        return jsonify({
            "success": True,
            "filename": safe_name,
            "extracted_text": extracted_text,
            "metadata": metadata,
            "privacy_notice": "Your resume was processed ephemerally in local memory and has not been stored or logged."
        })

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to process PDF: {str(e)}"}), 500
    finally:
        # Strict privacy safeguard: immediately delete temporary file
        if temp_path:
            resume_service.cleanup_temporary_file(temp_path)

@app.route("/api/job/analyze", methods=["POST"])
def api_job_analyze():
    """Analyze a pasted job description."""
    data = request.get_json(silent=True) or {}
    job_description = data.get("job_description", "").strip()

    if not job_description:
        return jsonify({"success": False, "error": "Please paste or type a job description to analyze."}), 400

    try:
        result = matching_service.analyze_job_description(job_description)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/matching/analyze", methods=["POST"])
def api_matching_analyze():
    """Compare resume text to job description and return score + improvement suggestions."""
    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not resume_text:
        return jsonify({"success": False, "error": "Resume text is missing. Please extract or paste your resume."}), 400
    if not job_description:
        return jsonify({"success": False, "error": "Job description is missing. Please paste the target job description."}), 400

    try:
        result = matching_service.match_resume_to_job(resume_text, job_description)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/cover-letter/generate", methods=["POST"])
def api_cover_letter_generate():
    """Generate a tailored cover letter."""
    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()
    company_name = data.get("company_name", "").strip()
    job_title = data.get("job_title", "").strip()
    tone = data.get("tone", "Professional").strip()

    if not company_name:
        return jsonify({"success": False, "error": "Company Name is required."}), 400
    if not job_title:
        return jsonify({"success": False, "error": "Job Title is required."}), 400
    if not resume_text:
        return jsonify({"success": False, "error": "Resume text is required to anchor claims truthfully."}), 400
    if not job_description:
        return jsonify({"success": False, "error": "Job description is required to tailor the letter."}), 400

    try:
        result = cover_letter_service.generate_cover_letter(
            resume_text=resume_text,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            tone=tone
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/recruiter-messages/generate", methods=["POST"])
def api_recruiter_messages_generate():
    """Generate concise recruiter/networking messages."""
    data = request.get_json(silent=True) or {}
    message_type = data.get("message_type", "Application Follow-up").strip()
    company_name = data.get("company_name", "").strip()
    job_title = data.get("job_title", "").strip()
    tone = data.get("tone", "Professional & Polite").strip()
    resume_text = data.get("resume_text", "").strip()
    recipient_name = data.get("recipient_name", "").strip()
    additional_notes = data.get("additional_notes", "").strip()

    try:
        result = recruiter_service.generate_message(
            message_type=message_type,
            company_name=company_name,
            job_title=job_title,
            tone=tone,
            resume_text=resume_text,
            recipient_name=recipient_name,
            additional_notes=additional_notes
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/interview/questions", methods=["POST"])
def api_interview_questions():
    """Generate role-specific interview questions and grounded answers."""
    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "").strip()
    job_description = data.get("job_description", "").strip()

    if not job_description:
        return jsonify({"success": False, "error": "Please provide a job description to tailor interview questions."}), 400

    try:
        result = interview_service.generate_interview_questions(
            resume_text=resume_text,
            job_description=job_description
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/interview/evaluate", methods=["POST"])
def api_interview_evaluate():
    """Evaluate candidate's answer submitted in practice mode."""
    data = request.get_json(silent=True) or {}
    job_title = data.get("job_title", "").strip()
    question = data.get("question", "").strip()
    candidate_answer = data.get("candidate_answer", "").strip()

    if not candidate_answer or len(candidate_answer) < 15:
        return jsonify({"success": False, "error": "Please type a fuller answer (at least 15 characters) to evaluate."}), 400

    try:
        result = interview_service.evaluate_practice_answer(
            job_title=job_title,
            question=question,
            candidate_answer=candidate_answer
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------------------------------------------------------------------
# Application Tracker CRUD APIs (SQLite)
# ---------------------------------------------------------------------------
@app.route("/api/applications", methods=["GET"])
def api_get_applications():
    """Fetch applications with optional filtering and search."""
    search = request.args.get("search", "").strip() or None
    status = request.args.get("status", "").strip() or None

    try:
        apps = get_applications(search=search, status=status)
        return jsonify({"success": True, "applications": apps})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/applications", methods=["POST"])
def api_create_application():
    """Create a new tracked application."""
    data = request.get_json(silent=True) or {}
    company = data.get("company", "").strip()
    role = data.get("role", "").strip()
    application_date = data.get("application_date", "").strip()
    job_link = data.get("job_link", "").strip()
    status = data.get("status", "Applied").strip()
    notes = data.get("notes", "").strip()

    if not company:
        return jsonify({"success": False, "error": "Company name is required."}), 400
    if not role:
        return jsonify({"success": False, "error": "Role title is required."}), 400
    if not application_date:
        return jsonify({"success": False, "error": "Application date is required."}), 400
    if status not in VALID_STATUSES:
        return jsonify({"success": False, "error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"}), 400

    try:
        new_id = add_application(
            company=company,
            role=role,
            application_date=application_date,
            job_link=job_link,
            status=status,
            notes=notes
        )
        return jsonify({
            "success": True,
            "message": "Application added successfully.",
            "application_id": new_id
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/applications/<int:app_id>", methods=["GET"])
def api_get_single_application(app_id):
    """Retrieve single application detail."""
    app_data = get_application_by_id(app_id)
    if not app_data:
        return jsonify({"success": False, "error": "Application not found."}), 404
    return jsonify({"success": True, "application": app_data})

@app.route("/api/applications/<int:app_id>", methods=["PUT"])
def api_update_application(app_id):
    """Update an application."""
    data = request.get_json(silent=True) or {}
    company = data.get("company", "").strip()
    role = data.get("role", "").strip()
    application_date = data.get("application_date", "").strip()
    job_link = data.get("job_link", "").strip()
    status = data.get("status", "Applied").strip()
    notes = data.get("notes", "").strip()

    if not company:
        return jsonify({"success": False, "error": "Company name is required."}), 400
    if not role:
        return jsonify({"success": False, "error": "Role title is required."}), 400
    if not application_date:
        return jsonify({"success": False, "error": "Application date is required."}), 400
    if status not in VALID_STATUSES:
        return jsonify({"success": False, "error": f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"}), 400

    try:
        updated = update_application(
            app_id=app_id,
            company=company,
            role=role,
            application_date=application_date,
            job_link=job_link,
            status=status,
            notes=notes
        )
        if not updated:
            return jsonify({"success": False, "error": "Application not found or no changes made."}), 404
        return jsonify({"success": True, "message": "Application updated successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/applications/<int:app_id>", methods=["DELETE"])
def api_delete_application(app_id):
    """Delete an application by ID."""
    try:
        deleted = delete_application(app_id)
        if not deleted:
            return jsonify({"success": False, "error": "Application not found."}), 404
        return jsonify({"success": True, "message": "Application deleted successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ---------------------------------------------------------------------------
# Prompt Showcase & Live Production Prompt Inspector API
# ---------------------------------------------------------------------------
@app.route("/api/prompts/live", methods=["GET"])
def api_live_prompts():
    """Inspect production prompt templates currently active in memory."""
    return jsonify({
        "success": True,
        "system_prompt": SYSTEM_PROMPT,
        "templates": {
            "job_analysis": JOB_ANALYSIS_USER_PROMPT_TEMPLATE,
            "resume_matching": RESUME_MATCHING_USER_PROMPT_TEMPLATE,
            "cover_letter": COVER_LETTER_USER_PROMPT_TEMPLATE,
            "recruiter_message": RECRUITER_MESSAGE_USER_PROMPT_TEMPLATE,
            "interview_prep": INTERVIEW_PREP_USER_PROMPT_TEMPLATE,
            "interview_evaluation": INTERVIEW_EVALUATION_USER_PROMPT_TEMPLATE
        }
    })

if __name__ == "__main__":
    # Local development server
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AI Job Application Assistant on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
