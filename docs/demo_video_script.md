# Assessment Demo Video Script (2–3 Minutes)

**Role:** AI Growth & Automation Associate\
**Company:** Gokul Infocare\
**Project:** AI Job Application Assistant\
**Target Duration:** 2 minutes 45 seconds\

---

## ⏱️ Video Timeline & Teleprompter Script

### 0:00 – 0:30 | Problem Statement & Introduction
**Visual:** Webcam on speaker, transitioning to the AI Job Application Assistant Dashboard on screen.

> *"Hello, Gokul Infocare team! My name is [Your Name], and this is my submission for the AI Growth & Automation Associate assessment.*
>
> *Fresh graduates and entry-level job seekers face a real challenge today: they struggle to align their resumes with technical job descriptions, fall into the trap of using hallucinated AI buzzwords, and lack an organized way to track their application pipeline.*
>
> *I built the **AI Job Application Assistant**—a full-stack, production-ready web platform that provides transparent skill matching, grounded document generation, role-specific interview simulation, and local SQLite application tracking."*

---

### 0:30 – 1:00 | Architecture, AI Tools & Prompt Engineering
**Visual:** Transition to the **Prompt Engineering Showcase** page (`/prompt-showcase`).

> *"For our technology stack, I chose Python and Flask with SQLite on the backend, alongside a modern, responsive HTML5 and Vanilla CSS frontend.*
>
> *For generative AI, we integrate Google Gemini through the official `google-genai` SDK, with a fully deterministic offline Demo Mode as a fallback.*
>
> *Our prompt engineering approach solves four critical risks:*
> 1. *We eliminate hallucination by requiring strict factual grounding in the candidate's resume.*
> 2. *We sandbox all user input within XML tags to neutralize prompt injection attacks.*
> 3. *We enforce structured JSON output schemas.*
> 4. *And as you can see right here on the screen, we feature a **Live Production Prompt Inspector** that allows anyone to inspect the exact prompts running in memory."*

---

### 1:00 – 2:15 | Live Application Demonstration
**Visual:** Screen recording showing rapid workflow through the key tools.

> **[Clicking Resume Analyzer]:**\
> *"First, in the Resume Analyzer, we upload a PDF resume. Using `pypdf`, text is extracted in-memory, scanned image PDFs are detected with clear alerts, and the temporary file is immediately scrubbed for privacy.*
>
> **[Clicking Resume Matcher & ATS]:**\
> *Next, we compare the resume against the target Gokul Infocare job posting. Notice our transparent match score calculation: 75% for required skills and 25% for preferred skills. It displays exact matching skills, missing areas, and ATS bullet recommendations that explicitly flag when candidate verification is required.*
>
> **[Clicking Cover Letter & Recruiter Messages]:**\
> *Moving to Cover Letter and Recruiter Messaging: candidates can generate authentic letters and outreach messages across four distinct tones, with one-click clipboard copying and `.txt` file downloading.*
>
> **[Clicking Interview Prep & Practice]:**\
> *In Interview Prep, the system generates six targeted Technical, HR, and Project questions with STAR-structured answers. Even better, our **Candidate Practice Sandbox** allows users to type an answer and receive real-time coaching feedback, scoring, and an improved delivery model.*
>
> **[Clicking Application Tracker]:**\
> *Finally, our Application Tracker provides complete CRUD management, status filtering, and live analytics, persisting everything locally in SQLite with parameterized queries."*

---

### 2:15 – 2:45 | Challenges, Testing, and Conclusion
**Visual:** Displaying the Terminal with `30 tests passed` and returning to camera.

> *"During development, a key challenge was Windows file locking during SQLite temporary test teardowns. We solved this by implementing a clean `get_db()` context manager with explicit connection closures, achieving a 100% pass rate across all 30 automated unit and integration tests.*
>
> *In terms of limitations, scanned image-only PDFs currently prompt users to provide selectable text rather than running heavyweight OCR locally, and match scores are deliberately framed as alignment tools rather than hiring guarantees.*
>
> *This project demonstrates end-to-end automation, defensive prompt engineering, and production software standards. Thank you for your time, and I look forward to contributing to Gokul Infocare!"*

---

## 🎬 Recording Tips for the Candidate
1. **Screen Resolution:** Record at 1080p (1920x1080) for crisp typography.
2. **Audio:** Use an external microphone or headset with background noise suppression.
3. **Pacing:** Speak at a steady, enthusiastic pace (~130 words per minute).
4. **Browser State:** Have the app open at `http://127.0.0.1:5000` with sample data already loaded for seamless transitions.
