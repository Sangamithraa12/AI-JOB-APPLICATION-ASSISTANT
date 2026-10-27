/**
 * Interview Preparation & Candidate Practice Mode Client Logic.
 */

document.addEventListener("DOMContentLoaded", () => {
  const intResume = document.getElementById("intResumeInput");
  const intJob = document.getElementById("intJobInput");
  const genBtn = document.getElementById("generateInterviewBtn");
  const sampleBtn = document.getElementById("loadSampleInterviewBtn");
  const qCard = document.getElementById("intQuestionsCard");
  const accordion = document.getElementById("questionsAccordion");
  const modeLabel = document.getElementById("intModeLabel");

  // Practice Mode Sandbox Elements
  const practiceRole = document.getElementById("practiceRoleInput");
  const practiceQuestion = document.getElementById("practiceQuestionInput");
  const candidateAnswer = document.getElementById("candidateAnswerInput");
  const evaluateBtn = document.getElementById("evaluateAnswerBtn");
  const evalCard = document.getElementById("evaluationFeedbackCard");
  const evalRating = document.getElementById("evalRatingBadge");
  const evalScore = document.getElementById("evalScoreText");
  const evalStrengths = document.getElementById("evalStrengthsList");
  const evalImprovements = document.getElementById("evalImprovementsList");
  const evalModelAnswer = document.getElementById("evalModelAnswerText");

  // Prepopulate from session/localStorage
  if (intResume && !intResume.value) {
    intResume.value = localStorage.getItem("shared_resume_text") || "";
  }
  if (intJob && !intJob.value) {
    intJob.value = localStorage.getItem("shared_job_desc") || "";
  }

  if (sampleBtn && intResume && intJob) {
    sampleBtn.addEventListener("click", () => {
      intResume.value = `ALEX MORGAN
Skills: Python, Flask, REST APIs, SQLite, Prompt Engineering, Automation, Software Testing, Git.
Experience: Engineered career assistant web application with pypdf text parsing and persistent SQLite databases; created automated data ingestion pipeline processing 5,000+ daily records with 100% test pass rates.`;
      intJob.value = `Company: Gokul Infocare
Role: AI Growth & Automation Associate
Required: Python, Flask, REST API development, Prompt Engineering, Automation pipelines, Software testing.
Responsibilities: Build automated microservices, evaluate LLM prompts with zero-hallucination guardrails, and write clean technical documentation.`;
      showToast("Sample interview context loaded!", "info");
    });
  }

  if (genBtn && intJob) {
    genBtn.addEventListener("click", async () => {
      const jobText = intJob.value.trim();
      const resumeText = intResume ? intResume.value.trim() : "";

      if (!jobText) {
        showToast("Please provide a job description to tailor interview questions.", "warning");
        return;
      }

      genBtn.disabled = true;
      genBtn.textContent = "Generating role questions & answers...";
      showToast("Generating grounded interview preparation pack...", "info");

      try {
        const res = await fetch("/api/interview/questions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_description: jobText,
            resume_text: resumeText
          })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          renderQuestions(result.data.questions || []);
          modeLabel.textContent = result.data.mode_label || "Preparation Pack Generated";
          qCard.style.display = "block";
          showToast("6 role-specific questions generated!", "success");
          qCard.scrollIntoView({ behavior: "smooth" });
        } else {
          showToast(result.error || "Failed to generate interview questions.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error generating interview questions.", "error");
      } finally {
        genBtn.disabled = false;
        genBtn.textContent = "Generate Interview Questions & Answers";
      }
    });
  }

  function renderQuestions(questions) {
    accordion.innerHTML = "";

    if (questions.length === 0) {
      accordion.innerHTML = "<p style='color: var(--text-muted);'>No questions returned.</p>";
      return;
    }

    questions.forEach((q, idx) => {
      const item = document.createElement("div");
      item.style.border = "1px solid var(--border-light)";
      item.style.borderRadius = "var(--radius-md)";
      item.style.background = "#FFFFFF";
      item.style.overflow = "hidden";
      item.style.boxShadow = "var(--shadow-sm)";

      let catBadgeColor = "background: #EFF6FF; color: var(--blue-primary);";
      if (q.category === "HR & Behavioral") {
        catBadgeColor = "background: #F5F3FF; color: #7C3AED;";
      } else if (q.category === "Project & Experience") {
        catBadgeColor = "background: #ECFDF5; color: #059669;";
      }

      item.innerHTML = `
        <div style="padding: 16px 20px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; background: #F8FAFC;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
          <div style="display: flex; align-items: center; gap: 12px; flex: 1;">
            <span style="font-weight: 700; font-size: 0.85rem; color: var(--text-muted);">Q${idx + 1}</span>
            <span style="font-size: 0.72rem; padding: 2px 8px; border-radius: 999px; font-weight: 600; ${catBadgeColor}">${q.category}</span>
            <strong style="font-size: 0.95rem; color: var(--navy-dark);">${q.question}</strong>
          </div>
          <span style="font-size: 0.8rem; color: var(--text-muted);">▼ Details</span>
        </div>

        <div style="padding: 20px; border-top: 1px solid var(--border-subtle); display: ${idx === 0 ? 'block' : 'none'};">
          <div style="margin-bottom: 14px;">
            <div style="font-size: 0.76rem; text-transform: uppercase; color: var(--blue-primary); font-weight: 700; margin-bottom: 6px;">
              ⭐ Grounded STAR Suggested Answer:
            </div>
            <div style="background: #F8FAFC; border-left: 3px solid var(--blue-primary); padding: 14px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 0.88rem; line-height: 1.6; color: var(--text-primary); white-space: pre-line;">${q.suggested_answer}</div>
          </div>

          <div class="form-grid-2" style="margin-bottom: 14px;">
            <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: var(--radius-sm); padding: 12px;">
              <div style="font-size: 0.75rem; font-weight: 700; color: #92400E; margin-bottom: 4px;">Anticipated Probing Follow-Up Questions:</div>
              <ul style="padding-left: 18px; font-size: 0.82rem; color: #78350F; line-height: 1.5;">
                ${(q.follow_up_questions || []).map(f => `<li>${f}</li>`).join('')}
              </ul>
            </div>

            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: var(--radius-sm); padding: 12px;">
              <div style="font-size: 0.75rem; font-weight: 700; color: var(--blue-primary); margin-bottom: 4px;">Strategic Points to Emphasize:</div>
              <ul style="padding-left: 18px; font-size: 0.82rem; color: #1E40AF; line-height: 1.5;">
                ${(q.key_points_to_emphasize || []).map(p => `<li>${p}</li>`).join('')}
              </ul>
            </div>
          </div>

          <div style="display: flex; justify-content: flex-end;">
            <button class="btn btn-secondary btn-sm practice-this-btn" data-question="${encodeURIComponent(q.question)}">
              🎙️ Practice Answering This Question →
            </button>
          </div>
        </div>
      `;

      accordion.appendChild(item);
    });

    // Attach click listener for Practice This Question buttons
    document.querySelectorAll(".practice-this-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const qText = decodeURIComponent(e.currentTarget.dataset.question);
        practiceQuestion.value = qText;
        candidateAnswer.focus();
        document.getElementById("practiceSandboxCard").scrollIntoView({ behavior: "smooth" });
        showToast("Question loaded into Practice Sandbox!", "info");
      });
    });
  }

  // -------------------------------------------------------------------------
  // Part 2: Candidate Practice Mode Sandbox Evaluation
  // -------------------------------------------------------------------------
  if (evaluateBtn && candidateAnswer) {
    evaluateBtn.addEventListener("click", async () => {
      const role = practiceRole.value.trim();
      const question = practiceQuestion.value.trim();
      const answer = candidateAnswer.value.trim();

      if (!answer || answer.length < 15) {
        showToast("Please type a more detailed practice answer (at least 15 characters).", "warning");
        return;
      }

      evaluateBtn.disabled = true;
      evaluateBtn.textContent = "Evaluating your response...";
      showToast("Assessing your answer structure and delivery...", "info");

      try {
        const res = await fetch("/api/interview/evaluate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_title: role,
            question: question,
            candidate_answer: answer
          })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          renderEvaluation(result.data);
          evalCard.style.display = "block";
          showToast("Evaluation complete!", "success");
          evalCard.scrollIntoView({ behavior: "smooth" });
        } else {
          showToast(result.error || "Failed to evaluate answer.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error evaluating answer.", "error");
      } finally {
        evaluateBtn.disabled = false;
        evaluateBtn.textContent = "Evaluate My Answer & Get Feedback";
      }
    });
  }

  function renderEvaluation(data) {
    evalRating.textContent = data.overall_rating || "Evaluated";
    if (data.overall_rating === "Strong") {
      evalRating.className = "status-badge Offer";
    } else if (data.overall_rating === "Satisfactory") {
      evalRating.className = "status-badge Assessment";
    } else {
      evalRating.className = "status-badge Interview";
    }

    evalScore.textContent = `Score: ${data.score || 75}/100`;

    evalStrengths.innerHTML = "";
    (data.strengths || []).forEach(s => {
      const li = document.createElement("li");
      li.textContent = s;
      evalStrengths.appendChild(li);
    });

    evalImprovements.innerHTML = "";
    (data.areas_for_improvement || []).forEach(i => {
      const li = document.createElement("li");
      li.textContent = i;
      evalImprovements.appendChild(li);
    });

    evalModelAnswer.textContent = data.improved_model_answer || "";
  }
});
