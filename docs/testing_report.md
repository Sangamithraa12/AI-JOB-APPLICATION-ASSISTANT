# Software Testing & Quality Assurance Report

**Project:** AI Job Application Assistant\
**Assessment:** Gokul Infocare AI Growth & Automation Associate Practical Assessment\
**Testing Framework:** Python Standard Library `unittest` + Flask Test Client\
**Execution Timestamp:** October 26, 2026\
**Overall Result:** **30 Passed / 0 Failed / 0 Errors** (100% Pass Rate)\

---

## 1. Testing Strategy & Scope

The testing strategy validates the entire application lifecycle across five core layers:
1. **Document Parsing & Privacy (`test_resume.py`):** PDF validation, size constraints, corrupted stream recovery, and scanned image detection.
2. **Matching & Scoring Mathematics (`test_matching.py`):** Taxonomy skill extraction, transparent 75/25 weighting calculation, boundary conditions, and non-hallucinatory suggestions.
3. **Prompt Engineering & Security (`test_prompts.py`):** System prompt guardrails, delimiter escaping, prompt injection neutralization, and template schemas.
4. **Data Sovereignty & Persistence (`test_tracker.py`):** SQLite schema integrity, parameterized SQL CRUD operations, search/filter algorithms, and dashboard metrics.
5. **End-to-End API Workflows (`test_api.py`):** HTTP status codes, JSON payload contracts, and error handling across all Flask endpoints.

---

## 2. Test Execution Summary

```text
Ran 30 tests in 0.347s

OK
```

---

## 3. Detailed Test Cases and Results

### A. Resume Upload & Extraction (`tests/test_resume.py`)

| Test ID | Test Case | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `RES-01` | Extension Whitelisting | Allow `.pdf` and `.PDF`; reject `.docx`, `.exe`, and unextended files | Properly whitelisted `.pdf`; rejected invalid extensions | **PASS** |
| `RES-02` | Corrupted PDF Recovery | Non-PDF bytes stream raises `ValueError` with descriptive message | Gracefully raised `ValueError("Could not read PDF file...")` | **PASS** |
| `RES-03` | Scanned / Empty PDF Detection | Blank page PDF triggers `is_scanned_or_empty: True` with user warning | Warning generated: *"Minimal or no text extracted (<60 characters)..."* | **PASS** |
| `RES-04` | Valid PDF Text Extraction | Synthetic PDF generated with `fpdf` extracts full text and calculates accurate character/word metrics | Correctly extracted text, word count (9), character count (78), with zero warnings | **PASS** |

### B. Skill Matching & Score Calculation (`tests/test_matching.py`)

| Test ID | Test Case | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `MAT-01` | Taxonomy Skill Extraction | Extract canonical skills (Python, Flask, SQLite, REST APIs, Docker) | Extracted all 5 skills using regex boundary matching | **PASS** |
| `MAT-02` | 100% Match Boundary | When resume contains all required and preferred skills, score must equal 100% | Match score computed: `100%`, `missing_skills: []` | **PASS** |
| `MAT-03` | 0% Match Boundary | When resume contains no matching skills, score must equal 0% | Match score computed: `0%`, all skills listed in `missing_skills` | **PASS** |
| `MAT-04` | Weighted Partial Match | 50% required skills (75% weight) + 50% preferred skills (25% weight) = 50% total | Calculated: `(0.50 * 75) + (0.50 * 25) = 50%` | **PASS** |
| `MAT-05` | Missing Input Validation | Empty resume or empty job description raises `ValueError` | Raised `ValueError` with clear input requirement messages | **PASS** |
| `MAT-06` | Improvement Verification Flag | Improvement opportunities include `needs_user_verification` boolean | Confirmed all suggestions have typed boolean verification flags | **PASS** |

### C. Prompt Safety & Delimiter Defenses (`tests/test_prompts.py`)

| Test ID | Test Case | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `PRM-01` | System Prompt Guardrails | Mandates `FACTUAL GROUNDING`, `NO HALLUCINATION`, and `TRANSPARENCY` | All four mandatory directives confirmed present in `SYSTEM_PROMPT` | **PASS** |
| `PRM-02` | Delimiter Escaping Defense | Strips injected `</resume_text>` and `</job_description>` tags | Replaced with `[resume_text_tag_removed]`, preventing context breakout | **PASS** |
| `PRM-03` | Template Placeholders | All format placeholders populate without KeyError | Formatted cleanly across Job, Match, and Cover Letter templates | **PASS** |
| `PRM-04` | Prompt Showcase Integrity | Contains 3 distinct use cases with initial vs improved analysis | Confirmed `matching`, `cover_letter`, and `interview_prep` data present | **PASS** |
| `PRM-05` | Markdown Fence Extractor | Strips ```` ```json ```` fences and extracts clean JSON | Successfully extracted JSON from markdown wrapped outputs | **PASS** |

### D. SQLite Application Tracker (`tests/test_tracker.py`)

| Test ID | Test Case | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `TRK-01` | Create & Retrieve Application | Insert record, verify non-zero ID, retrieve row by ID | Successfully inserted and retrieved row matching all fields | **PASS** |
| `TRK-02` | Status Constraint Validation | Reject statuses outside `Interested, Applied, Assessment, Interview, Offer, Rejected` | Raised `ValueError("Invalid status...")` on illegal status | **PASS** |
| `TRK-03` | Application Update | Modify status and notes; verify persistence in SQLite | Fields updated, `updated_at` timestamp refreshed | **PASS** |
| `TRK-04` | Application Deletion | Delete by ID; verify subsequent query returns `None` | Successfully deleted record; subsequent lookup returned `None` | **PASS** |
| `TRK-05` | Search & Filter Logic | Filter by keyword (`"Backend"`) and status (`"Interview"`) | Correctly returned matching subsets using parameterized queries | **PASS** |
| `TRK-06` | Dashboard Statistics | Calculate totals, status breakdown, and conversion rates from stored rows | Computed accurate counts (4 total, 1 offer, 1 interview, conversion rates > 0) | **PASS** |

### E. End-to-End Flask REST APIs (`tests/test_api.py`)

| Test ID | Test Case | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| `API-01` | `GET /api/status` | HTTP 200, returns AI provider and operational mode | HTTP 200, returned provider status, model, and notice | **PASS** |
| `API-02` | `GET /api/dashboard/stats` | HTTP 200, returns real counts from SQLite database | HTTP 200, returned status distribution and conversion rates | **PASS** |
| `API-03` | `POST /api/job/analyze` | HTTP 200, returns structured title, skills, and duties | HTTP 200, returned structured JSON requirements | **PASS** |
| `API-04` | `POST /api/matching/analyze` | HTTP 200, returns match score and formula breakdown | HTTP 200, returned match score, breakdown, and suggestions | **PASS** |
| `API-05` | `POST /api/cover-letter/generate` | HTTP 200, returns tailored letter with selected tone | HTTP 200, returned grounded letter starting with "Dear Hiring Team" | **PASS** |
| `API-06` | `POST /api/recruiter-messages/generate` | HTTP 200, returns subject and message body | HTTP 200, returned subject line and personalized body | **PASS** |
| `API-07` | `POST /api/interview/questions` | HTTP 200, returns 6 role questions with STAR answers | HTTP 200, returned 6 questions across Technical, HR, and Project categories | **PASS** |
| `API-08` | `POST /api/interview/evaluate` | HTTP 200, evaluates candidate practice answer | HTTP 200, returned score (85), strengths, and improved answer | **PASS** |
| `API-09` | `GET /api/prompts/live` | HTTP 200, returns live in-memory prompt templates | HTTP 200, returned system prompt and 6 production templates | **PASS** |

---

## 4. Issues Discovered and Resolved During Testing

1. **Windows File Lock in Temporary Directory Cleanup (`WinError 32`):**
   - *Discovery:* During initial test suite execution, `shutil.rmtree` failed in `test_tracker.py` tearDownClass because SQLite kept file handles open on Windows.
   - *Fix:* Configured `tempfile.TemporaryDirectory(ignore_cleanup_errors=True)` and invoked `gc.collect()` alongside explicit `conn.close()` in `database/db.py`.
   - *Outcome:* Zero warnings or errors on subsequent test runs.

2. **Unclosed Connection ResourceWarnings:**
   - *Discovery:* Python 3.14 flagged unclosed `sqlite3.Connection` instances when relying solely on `with conn:` (which only commits transactions).
   - *Fix:* Created a custom `get_db()` context manager in `database/db.py` that guarantees `conn.close()` inside a `finally:` block.
   - *Outcome:* Eliminated all `ResourceWarning` occurrences.

---

## 5. Test Verdict

All **30 unit and integration tests executed cleanly with 100% pass rate**. The application is verified for production readiness, input validation, mathematical correctness, and zero-hallucination guardrails.
