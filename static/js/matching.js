/**
 * Job Description Analysis & Resume-to-Job Matching Client Logic.
 */

const SAMPLE_GOKUL_JOB_DESC = `Job Title: AI Growth & Automation Associate
Company: Gokul Infocare
Location: Hybrid / Chennai, India
Experience: Entry-Level / Fresh Graduate (0-2 years)

About the Role:
Gokul Infocare is seeking a high-energy AI Growth & Automation Associate to help scale our automation workflows and software delivery pipelines. You will collaborate directly with our engineering and growth teams to automate repetitive tasks, evaluate AI prompts, and build robust software integrations.

Required Skills & Qualifications:
- Proficiency in Python programming and backend frameworks (Flask, FastAPI, or Django)
- Understanding of RESTful API design and database persistence (SQL, SQLite, or PostgreSQL)
- Hands-on experience with modern AI concepts: Prompt Engineering, LLM integration, and automation tools
- Strong software testing, debugging, and Git version control practices
- Proactive problem-solving abilities and clear technical communication skills

Preferred / Nice-to-Have Skills:
- Experience with web technologies: HTML5, CSS3, and JavaScript
- Exposure to containerization (Docker) or cloud deployments (AWS / GCP)
- Familiarity with data analysis libraries (Pandas, NumPy)

Key Responsibilities:
- Design, test, and maintain automated application workflows and microservices.
- Formulate, test, and iterate on AI prompt templates with zero-hallucination guardrails.
- Create transparent technical documentation, test reports, and process walkthroughs.
- Assist in optimizing internal operations and client automation pipelines.`;

const SAMPLE_CANDIDATE_RESUME = `ALEX MORGAN
Email: alex.morgan@example.com | Phone: +1-555-0199 | Location: Boston, MA
LinkedIn: linkedin.com/in/alexmorgan-dev | GitHub: github.com/alexmorgan

PROFESSIONAL SUMMARY
Curious and results-driven Computer Science graduate with hands-on project experience in Python, Flask, and REST API development. Passionate about automating repetitive workflows, engineering reliable prompts for large language models, and writing well-tested, maintainable code.

CORE TECHNICAL SKILLS
- Programming: Python, JavaScript, HTML5, CSS3, SQL, SQLite
- Frameworks & Tools: Flask, Git, GitHub, REST APIs, JSON
- AI & Automation: Prompt Engineering, LLM Integration, Workflow Automation
- Data & Testing: Pandas, Software Testing, Unit Testing, Agile methodologies

TECHNICAL PROJECTS
AI Career Companion | Python, Flask, SQLite, HTML5, CSS3
- Developed an end-to-end web application that analyzes job postings and extracts key requirements with transparent skill matching.
- Integrated LLM APIs using defensive XML-delimited prompt templates, eliminating prompt injection risks and reducing hallucination.
- Implemented persistent application tracking using SQLite with parameterized queries, ensuring zero SQL injection vulnerabilities.
- Authored automated test suites covering file validation, edge cases, and API error states with 100% test pass rates.

Automated Data Ingestion Pipeline | Python, Pandas, SQLite
- Built an automated data collection and cleaning script processing 5,000+ daily CSV records.
- Optimized query execution with index creation and structured validation, reducing runtimes by 35%.

EDUCATION
Bachelor of Science in Computer Science
State University of Technology | Graduated: May 2026
Relevant Coursework: Data Structures & Algorithms, Database Systems, Software Engineering, Artificial Intelligence.`;

document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------------------------------------------------
  // Part 1: Job Description Parser Page Logic (/job-analyzer)
  // -------------------------------------------------------------------------
  const loadSampleJobBtn = document.getElementById("loadSampleJobBtn");
  const jobInput = document.getElementById("jobDescriptionInput");
  const analyzeJobBtn = document.getElementById("analyzeJobBtn");
  const jobResultCard = document.getElementById("jobResultCard");
  const sendJobToMatcherBtn = document.getElementById("sendJobToMatcherBtn");

  if (loadSampleJobBtn && jobInput) {
    loadSampleJobBtn.addEventListener("click", () => {
      jobInput.value = SAMPLE_GOKUL_JOB_DESC;
      showToast("Gokul Infocare assessment job description loaded!", "info");
    });
  }

  if (analyzeJobBtn && jobInput) {
    analyzeJobBtn.addEventListener("click", async () => {
      const text = jobInput.value.trim();
      if (!text) {
        showToast("Please paste or type a job description first.", "warning");
        return;
      }

      analyzeJobBtn.disabled = true;
      analyzeJobBtn.textContent = "Analyzing requirements...";

      try {
        const res = await fetch("/api/job/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_description: text })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          renderJobAnalysis(result.data);
          showToast("Job description analyzed successfully!", "success");
          localStorage.setItem("shared_job_desc", text);
          jobResultCard.style.display = "block";
          jobResultCard.scrollIntoView({ behavior: "smooth" });
        } else {
          showToast(result.error || "Failed to analyze job description.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error analyzing job description.", "error");
      } finally {
        analyzeJobBtn.disabled = false;
        analyzeJobBtn.textContent = "Analyze Job Description";
      }
    });
  }

  function renderJobAnalysis(data) {
    document.getElementById("parsedJobTitle").textContent = data.job_title || "Standard Role";
    document.getElementById("parsedCompany").textContent = data.company_name || "Target Employer";
    document.getElementById("parsedExpLevel").textContent = data.experience_level || "Not specified";
    document.getElementById("jobModeLabel").textContent = data.mode_label || "Analysis Complete";

    // Required Skills
    const reqCont = document.getElementById("requiredSkillsContainer");
    reqCont.innerHTML = "";
    (data.required_skills || []).forEach((skill) => {
      const span = document.createElement("span");
      span.className = "skill-tag";
      span.textContent = skill;
      reqCont.appendChild(span);
    });

    // Preferred Skills
    const prefCont = document.getElementById("preferredSkillsContainer");
    prefCont.innerHTML = "";
    if (data.preferred_skills && data.preferred_skills.length > 0) {
      data.preferred_skills.forEach((skill) => {
        const span = document.createElement("span");
        span.className = "skill-tag";
        span.style.background = "#F1F5F9";
        span.style.color = "var(--text-secondary)";
        span.textContent = skill;
        prefCont.appendChild(span);
      });
    } else {
      prefCont.innerHTML = "<span style='font-size: 0.8rem; color: var(--text-muted);'>No distinct preferred skills listed.</span>";
    }

    // Responsibilities
    const respList = document.getElementById("responsibilitiesList");
    respList.innerHTML = "";
    (data.key_responsibilities || []).forEach((resp) => {
      const li = document.createElement("li");
      li.textContent = resp;
      respList.appendChild(li);
    });

    // Inferred Competencies
    const infList = document.getElementById("inferredList");
    infList.innerHTML = "";
    (data.inferred_competencies || []).forEach((comp) => {
      const li = document.createElement("li");
      li.textContent = comp;
      infList.appendChild(li);
    });
  }

  if (sendJobToMatcherBtn && jobInput) {
    sendJobToMatcherBtn.addEventListener("click", () => {
      if (!jobInput.value.trim()) return;
      localStorage.setItem("shared_job_desc", jobInput.value.trim());
      window.location.href = "/matching";
    });
  }

  // -------------------------------------------------------------------------
  // Part 2: Resume-to-Job Matching Page Logic (/matching)
  // -------------------------------------------------------------------------
  const matchResumeInput = document.getElementById("matchResumeInput");
  const matchJobInput = document.getElementById("matchJobInput");
  const runMatchBtn = document.getElementById("runMatchBtn");
  const matchResultsCard = document.getElementById("matchResultsCard");
  const loadSampleMatchingDataBtn = document.getElementById("loadSampleMatchingDataBtn");

  // Prepopulate from session/localStorage if available
  if (matchResumeInput) {
    const cachedResume = localStorage.getItem("shared_resume_text");
    if (cachedResume && !matchResumeInput.value) {
      matchResumeInput.value = cachedResume;
      document.getElementById("matchResumeCharCount").textContent = `${cachedResume.length} chars`;
    }
    matchResumeInput.addEventListener("input", () => {
      document.getElementById("matchResumeCharCount").textContent = `${matchResumeInput.value.length} chars`;
    });
  }

  if (matchJobInput) {
    const cachedJob = localStorage.getItem("shared_job_desc");
    if (cachedJob && !matchJobInput.value) {
      matchJobInput.value = cachedJob;
      document.getElementById("matchJobCharCount").textContent = `${cachedJob.length} chars`;
    }
    matchJobInput.addEventListener("input", () => {
      document.getElementById("matchJobCharCount").textContent = `${matchJobInput.value.length} chars`;
    });
  }

  if (loadSampleMatchingDataBtn && matchResumeInput && matchJobInput) {
    loadSampleMatchingDataBtn.addEventListener("click", () => {
      matchResumeInput.value = SAMPLE_CANDIDATE_RESUME;
      matchJobInput.value = SAMPLE_GOKUL_JOB_DESC;
      document.getElementById("matchResumeCharCount").textContent = `${SAMPLE_CANDIDATE_RESUME.length} chars`;
      document.getElementById("matchJobCharCount").textContent = `${SAMPLE_GOKUL_JOB_DESC.length} chars`;
      showToast("Sample candidate profile & Gokul Infocare job loaded!", "info");
    });
  }

  if (runMatchBtn && matchResumeInput && matchJobInput) {
    runMatchBtn.addEventListener("click", async () => {
      const resume = matchResumeInput.value.trim();
      const job = matchJobInput.value.trim();

      if (!resume) {
        showToast("Please provide your resume text.", "warning");
        return;
      }
      if (!job) {
        showToast("Please provide the target job description.", "warning");
        return;
      }

      runMatchBtn.disabled = true;
      runMatchBtn.textContent = "Analyzing skill match...";
      showToast("Comparing resume to job description...", "info");

      try {
        const res = await fetch("/api/matching/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ resume_text: resume, job_description: job })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          renderMatchResults(result.data);
          showToast("Match calculation complete!", "success");
          matchResultsCard.style.display = "block";
          matchResultsCard.scrollIntoView({ behavior: "smooth" });
        } else {
          showToast(result.error || "Failed to calculate match score.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error calculating match.", "error");
      } finally {
        runMatchBtn.disabled = false;
        runMatchBtn.textContent = "Analyze Match & Suggest ATS Improvements";
      }
    });
  }

  function renderMatchResults(data) {
    document.getElementById("matchModeLabel").textContent = data.mode_label || "Score Calculated";
    document.getElementById("matchScoreNum").textContent = `${data.match_score}%`;
    document.getElementById("scoreExplanationText").textContent = data.score_explanation || "";
    document.getElementById("experienceAlignmentText").textContent = data.experience_alignment || "";

    // Matching Skills tags
    const matchCont = document.getElementById("matchingSkillsList");
    matchCont.innerHTML = "";
    if (data.matching_skills && data.matching_skills.length > 0) {
      data.matching_skills.forEach((skill) => {
        const span = document.createElement("span");
        span.className = "skill-tag match";
        span.textContent = `✓ ${skill}`;
        matchCont.appendChild(span);
      });
    } else {
      matchCont.innerHTML = "<span style='font-size: 0.8rem; color: var(--text-muted);'>No direct skill keywords overlapped.</span>";
    }

    // Missing Skills tags
    const missCont = document.getElementById("missingSkillsList");
    missCont.innerHTML = "";
    if (data.missing_skills && data.missing_skills.length > 0) {
      data.missing_skills.forEach((skill) => {
        const span = document.createElement("span");
        span.className = "skill-tag missing";
        span.textContent = `+ ${skill}`;
        missCont.appendChild(span);
      });
    } else {
      missCont.innerHTML = "<span style='font-size: 0.8rem; color: #059669;'>Zero required skills missing!</span>";
    }

    // Improvement Opportunities
    const impCont = document.getElementById("improvementsContainer");
    impCont.innerHTML = "";
    const opps = data.improvement_opportunities || [];

    if (opps.length === 0) {
      impCont.innerHTML = "<p style='font-size: 0.85rem; color: var(--text-muted);'>No immediate wording improvements flagged.</p>";
      return;
    }

    opps.forEach((opp) => {
      const card = document.createElement("div");
      card.style.background = "#FFFFFF";
      card.style.border = "1px solid var(--border-light)";
      card.style.borderRadius = "var(--radius-md)";
      card.style.padding = "16px";
      card.style.boxShadow = "var(--shadow-sm)";

      const badgeHtml = opp.needs_user_verification
        ? `<span style="font-size: 0.72rem; background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; padding: 2px 8px; border-radius: 999px; font-weight: 600;">⚠️ Needs Candidate Verification</span>`
        : `<span style="font-size: 0.72rem; background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; padding: 2px 8px; border-radius: 999px; font-weight: 600;">✅ Grounded in Resume</span>`;

      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <h5 style="font-size: 0.92rem; font-weight: 700; color: var(--navy-dark);">${opp.section}</h5>
          ${badgeHtml}
        </div>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 8px;"><strong>Issue:</strong> ${opp.current_issue}</p>
        <div style="background: #F8FAFC; border-left: 3px solid var(--blue-primary); padding: 10px 14px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0;">
          <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--blue-primary); font-weight: 700; margin-bottom: 4px;">Recommended ATS Bullet Wording:</div>
          <div style="font-size: 0.88rem; color: var(--text-primary); font-family: inherit; line-height: 1.5;">${opp.suggested_wording}</div>
        </div>
      `;
      impCont.appendChild(card);
    });
  }
});
