# ⚡ AI Job Application Assistant

**Practical Assessment Submission for Gokul Infocare**\
**Role:** AI Growth & Automation Associate\
**Author:** Senior Full-Stack & AI Engineer Candidate\

[![Python Version](https://img.shields.io/badge/Python-3.14%2B-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-SQLite3-003B57.svg)](https://sqlite.org/)
[![AI Integration](https://img.shields.io/badge/AI%20SDK-Google%20GenAI-4285F4.svg)](https://aistudio.google.com/)
[![Tests Passing](https://img.shields.io/badge/Tests-30%20Passed%20%7C%20100%25-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/License-MIT-gray.svg)](#license)

---

## 📖 1. Project Overview & Problem Statement

### The Problem
Job seekers, fresh graduates, and career transitioners face three persistent barriers when applying for technical roles:
1. **Resume-Job Misalignment:** Candidates struggle to accurately identify missing competencies and tailor their experience without creating generic buzzwords.
2. **AI Embellishment & Hallucination:** Naive AI tools invent work history, company titles, and unearned certifications, placing candidates at severe risk during technical interviews.
3. **Application Chaos:** Job applications, interview dates, outreach messages, and status updates are scattered across disjointed spreadsheets and inboxes.

### The Solution
The **AI Job Application Assistant** is a full-stack, production-grade career platform engineered to solve these problems through:
- **Transparent Skill Matching:** Mathematical breakdown ($75\%$ required skills $+ 25\%$ preferred skills) explicitly presented as an editorial alignment tool, never a hiring guarantee.
- **Defensive Prompt Engineering:** Strict zero-hallucination guardrails, XML-delimiter input sandboxing, and output verification tagging.
- **Dual-Engine Architecture:** Seamless integration with Google Gemini via the official `google-genai` SDK, backed by a 100% offline deterministic rule engine for truthful fallback.
- **Local Data Sovereignty:** Ephemeral resume parsing in memory with immediate file deletion, and persistent local SQLite tracking.

---

## 🌟 2. Key Features

| Feature | Description | Key Capabilities |
| :--- | :--- | :--- |
| **A. Resume Analyzer** | Secure PDF resume extraction | Validates extension/size, extracts text with `pypdf`, detects scanned/empty PDFs, zero permanent storage. |
| **B. Job Description Parser** | Structured requirements extraction | Identifies job title, required/preferred skills, core duties, and distinguishes explicit from inferred requirements. |
| **C. Resume-to-Job Matcher** | Transparent skill alignment | Calculates documented match score, flags matching and missing skills, and details mathematical formulas. |
| **D. ATS Improvement Engine** | Non-hallucinatory wording optimizer | Provides grounded ATS bullet suggestions with `needs_user_verification` flags for unverified claims. |
| **E. Cover Letter Generator** | Role-tailored application letters | Customizes letters across 4 tones (Professional, Enthusiastic, Confident, Direct); supports live editing, copy, and `.txt` download. |
| **F. Recruiter Message Generator** | High-impact networking messages | Formulates outreach for 5 key scenarios (Follow-up, Cold Inquiry, Referral Request, Recruiter InMail, Rescheduling). |
| **G. Interview Preparation & Practice** | Role-specific Q&A + Practice Sandbox | Generates 6 Technical, HR, and Project questions with STAR answers + an interactive Practice Sandbox with instant scoring and coaching. |
| **H. Application Tracker** | Persistent local SQLite pipeline | Complete CRUD with status filtering (`Interested`, `Applied`, `Assessment`, `Interview`, `Offer`, `Rejected`), search, and conversion analytics. |
| **I. Prompt Engineering Showcase** | Iterative prompt documentation | Side-by-side analysis of 3 use cases (Initial vs Improved) + a **Live Production Prompt Inspector** displaying in-memory active templates. |
| **J. Live Analytics Dashboard** | Real-time pipeline metrics | Dynamic counts, conversion ratios, and quick-action workflow accelerators calculated directly from SQLite. |

---

## 🏛️ 3. System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│             Frontend (HTML5 + CSS3 + Vanilla JS)            │
│  SaaS Dashboard • Drag-and-Drop PDF • Interactive Modals    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Fetch API (REST JSON)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application (app.py)               │
│         Route Handlers • Parameterized Validation • CORS    │
└──────────┬───────────────────┬───────────────────┬──────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌────────────────────┐ ┌────────────────────┐ ┌───────────────┐
│  pypdf Extraction  │ │  services/         │ │  database/    │
│  (In-Memory Parse) │ │  - matching_service│ │  (SQLite3     │
│  Immediate Cleanup │ │  - prompt_templates│ │   job_tracker │
└────────────────────┘ │  - cover_letter    │ │   .db)        │
                       │  - interview_prep  │ └───────────────┘
                       └─────────┬──────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
     [Live AI: Google Gemini]        [Demo Mode: Deterministic Engine]
    (Official google-genai SDK)       (100% Offline Rule/Taxonomy)
```

---

## 💻 4. Technologies Used

- **Backend:** Python 3.14, Flask 3.1.3, Werkzeug
- **Database:** SQLite3 (Local file-based persistence with parameterized SQL)
- **Document Processing:** `pypdf` 6.21.2, `fpdf` 1.7.2
- **Generative AI:** Google GenAI Official SDK (`google-genai` 2.33.0), REST fallbacks
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Custom SaaS Design System), Vanilla JavaScript (ES6+)
- **Testing:** Python Standard Library `unittest` (30 automated test cases)

---

## 🚀 5. Installation & Setup Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/ai-job-application-assistant.git
cd ai-job-application-assistant
```

### Step 2: Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the `.env.example` template to `.env`:
```powershell
cp .env.example .env
```
Open `.env` and set your preferred configuration:
```env
# Free API Key from https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here

# Model Selection
GEMINI_MODEL=gemini-2.5-flash

# Force Demo Mode (true/false)
DEMO_MODE=false

# Port & Secret
PORT=5000
SECRET_KEY=your-dev-secret-key
```

> **Note on Demo Mode:** If you do not have an API key right now, simply leave `GEMINI_API_KEY=` blank. The application will start in **honest Demo Mode**, powered by the local deterministic rule engine. All features will work!

---

## 🏃 6. Running the Application

Start the local development server:
```powershell
python app.py
```
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 7. Running Tests

Execute the automated test suite covering all 30 unit and integration cases:
```powershell
python -m unittest discover tests -v
```

### Expected Output
```text
test_cover_letter_generate_endpoint ... ok
test_dashboard_stats_endpoint ... ok
test_interview_evaluate_endpoint ... ok
test_interview_questions_endpoint ... ok
test_job_analyze_endpoint ... ok
test_live_prompts_endpoint ... ok
test_matching_analyze_endpoint ... ok
test_recruiter_message_generate_endpoint ... ok
test_status_endpoint ... ok
test_calculate_match_score_full_match ... ok
test_calculate_match_score_weighted_partial ... ok
test_calculate_match_score_zero_match ... ok
test_extract_skills_rule_based ... ok
test_improvement_opportunities_structure ... ok
test_match_missing_inputs ... ok
test_delimiter_sanitization_defense ... ok
test_json_extractor_helper ... ok
test_prompt_showcase_completeness ... ok
test_system_prompt_guardrails ... ok
test_template_placeholders ... ok
test_allowed_file ... ok
test_empty_corrupted_stream ... ok
test_scanned_or_empty_pdf_detection ... ok
test_valid_pdf_text_extraction ... ok
test_add_and_retrieve_application ... ok
test_dashboard_statistics ... ok
test_delete_application ... ok
test_invalid_status_rejection ... ok
test_search_and_filter ... ok
test_update_application ... ok

----------------------------------------------------------------------
Ran 30 tests in 0.347s

OK
```

---

## 🛡️ 8. Privacy & Security Safeguards

- **Zero Permanent Resume Retention:** Resumes are processed ephemerally in-memory and deleted immediately upon text extraction.
- **Local Data Sovereignty:** Tracked jobs and personal notes reside solely inside `database/job_tracker.db` on your local disk.
- **SQL Injection Prevention:** 100% of database interactions use parameterized queries (`?` placeholders).
- **Prompt Injection Defense:** Delimiter escaping neuters malicious `</resume_text>` tags in untrusted user inputs.
- **Secret Safety:** API keys are restricted to the server-side `.env` file and excluded via `.gitignore`.

---

## ⚠️ 9. Limitations & Ethical Disclaimers

1. **Alignment Tool, Not Hiring Guarantee:** The match score reflects lexical and contextual skill overlap between the resume and job description. It does not measure emotional intelligence, portfolio execution, or hiring likelihood.
2. **Scanned Image PDFs:** PDFs containing pure image scans without selectable text trigger a warning suggesting the user supply a selectable text document or paste text directly.
3. **No Automated Embellishment:** The system will never fabricate experience. If a job requires Kubernetes and the candidate lacks it, the tool guides the candidate to address it via learning projects rather than inventing false claims.

---

## 📦 10. GitHub Publishing Instructions

To push this codebase to a public GitHub repository safely:

```powershell
# 1. Initialize git
git init

# 2. Verify .env and database are excluded
git status

# 3. Add files and commit
git add .
git commit -m "Initial commit: Complete AI Job Application Assistant for Gokul Infocare assessment"

# 4. Link your remote repository and push
git branch -M main
git remote add origin https://github.com/<your-username>/ai-job-application-assistant.git
git push -u origin main
```

---

## 📄 License
Released under the [MIT License](LICENSE). Built for the Gokul Infocare practical assessment.
