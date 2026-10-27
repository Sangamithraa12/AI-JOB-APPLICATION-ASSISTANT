/**
 * Cover Letter & Recruiter Message Generator Client Logic.
 */

document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------------------------------------------------
  // Part 1: Cover Letter Generator (/cover-letter)
  // -------------------------------------------------------------------------
  const clCompany = document.getElementById("clCompanyInput");
  const clRole = document.getElementById("clRoleInput");
  const clTone = document.getElementById("clToneSelect");
  const clResume = document.getElementById("clResumeInput");
  const clJob = document.getElementById("clJobInput");
  const clGenBtn = document.getElementById("generateCoverLetterBtn");
  const clOutputCard = document.getElementById("clOutputCard");
  const clOutputTextarea = document.getElementById("clOutputTextarea");
  const clModeLabel = document.getElementById("clModeLabel");
  const clCopyBtn = document.getElementById("copyCoverLetterBtn");
  const clDownloadBtn = document.getElementById("downloadCoverLetterBtn");
  const loadSampleCoverBtn = document.getElementById("loadSampleCoverLetterBtn");

  // Restore cached resume and JD if available
  if (clResume && !clResume.value) {
    clResume.value = localStorage.getItem("shared_resume_text") || "";
  }
  if (clJob && !clJob.value) {
    clJob.value = localStorage.getItem("shared_job_desc") || "";
  }

  if (loadSampleCoverBtn && clCompany && clRole) {
    loadSampleCoverBtn.addEventListener("click", () => {
      clCompany.value = "Gokul Infocare";
      clRole.value = "AI Growth & Automation Associate";
      clTone.value = "Professional";
      if (!clResume.value.trim()) {
        clResume.value = `ALEX MORGAN
Core Skills: Python, Flask, REST APIs, SQLite, Prompt Engineering, LLM Integration, Workflow Automation, Software Testing, Git.
Experience: Developed end-to-end web applications with transparent skill matching and persistent SQLite databases; built automated data pipelines processing 5,000+ daily records with 100% test pass rates.`;
      }
      if (!clJob.value.trim()) {
        clJob.value = `Company: Gokul Infocare
Role: AI Growth & Automation Associate
Required: Python, Flask, REST APIs, SQLite, Prompt Engineering, Automation, Testing.
Duties: Build and test automated software pipelines, formulate prompt templates with guardrails, and write clean technical documentation.`;
      }
      showToast("Sample application details loaded!", "info");
    });
  }

  if (clGenBtn && clCompany && clRole && clResume && clJob) {
    clGenBtn.addEventListener("click", async () => {
      const company = clCompany.value.trim();
      const role = clRole.value.trim();
      const resume = clResume.value.trim();
      const job = clJob.value.trim();
      const tone = clTone.value;

      if (!company || !role) {
        showToast("Please provide both Company Name and Job Title.", "warning");
        return;
      }
      if (!resume) {
        showToast("Resume text is required to anchor claims truthfully.", "warning");
        return;
      }
      if (!job) {
        showToast("Job description is required to tailor the letter.", "warning");
        return;
      }

      clGenBtn.disabled = true;
      clGenBtn.textContent = "Crafting tailored letter...";
      showToast("Generating authentic cover letter...", "info");

      try {
        const res = await fetch("/api/cover-letter/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            company_name: company,
            job_title: role,
            tone: tone,
            resume_text: resume,
            job_description: job
          })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          clOutputTextarea.value = result.data.cover_letter;
          clModeLabel.textContent = `${result.data.mode_label || 'Generated'} | Tone: ${result.data.tone}`;
          clOutputCard.style.display = "block";
          showToast("Cover letter generated!", "success");
          clOutputCard.scrollIntoView({ behavior: "smooth" });
        } else {
          showToast(result.error || "Failed to generate cover letter.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error generating cover letter.", "error");
      } finally {
        clGenBtn.disabled = false;
        clGenBtn.textContent = "Generate Tailored Cover Letter";
      }
    });
  }

  // Copy cover letter
  if (clCopyBtn && clOutputTextarea) {
    clCopyBtn.addEventListener("click", () => {
      if (!clOutputTextarea.value.trim()) return;
      navigator.clipboard.writeText(clOutputTextarea.value)
        .then(() => showToast("Cover letter copied to clipboard!", "success"))
        .catch(() => showToast("Could not access clipboard.", "error"));
    });
  }

  // Download cover letter as .txt
  if (clDownloadBtn && clOutputTextarea) {
    clDownloadBtn.addEventListener("click", () => {
      const text = clOutputTextarea.value;
      if (!text.trim()) return;

      const company = (clCompany && clCompany.value.trim()) ? clCompany.value.trim().replace(/\s+/g, "_") : "Company";
      const filename = `Cover_Letter_${company}.txt`;

      const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showToast(`Downloaded ${filename}!`, "success");
    });
  }

  // -------------------------------------------------------------------------
  // Part 2: Recruiter Message Generator (/recruiter-messages)
  // -------------------------------------------------------------------------
  const msgType = document.getElementById("msgTypeSelect");
  const msgTone = document.getElementById("msgToneSelect");
  const msgCompany = document.getElementById("msgCompanyInput");
  const msgRole = document.getElementById("msgRoleInput");
  const msgRecipient = document.getElementById("msgRecipientInput");
  const msgNotes = document.getElementById("msgNotesInput");
  const msgResume = document.getElementById("msgResumeInput");
  const msgGenBtn = document.getElementById("generateRecruiterMsgBtn");
  const msgOutputCard = document.getElementById("msgOutputCard");
  const msgSubjectOutput = document.getElementById("msgSubjectOutput");
  const msgBodyOutput = document.getElementById("msgBodyOutput");
  const msgModeLabel = document.getElementById("msgModeLabel");
  const msgCopyBtn = document.getElementById("copyRecruiterMsgBtn");
  const loadSampleRecruiterBtn = document.getElementById("loadSampleRecruiterBtn");

  if (loadSampleRecruiterBtn && msgCompany && msgRole) {
    loadSampleRecruiterBtn.addEventListener("click", () => {
      msgCompany.value = "Gokul Infocare";
      msgRole.value = "AI Growth & Automation Associate";
      msgRecipient.value = "Technical Hiring Team";
      msgType.value = "Application Follow-up";
      msgTone.value = "Professional & Polite";
      msgNotes.value = "Submitted technical assignment yesterday; keen on automation initiatives.";
      msgResume.value = "Skills: Python, Flask, Prompt Engineering, SQLite, REST APIs.";
      showToast("Sample recruiter context loaded!", "info");
    });
  }

  if (msgGenBtn && msgCompany && msgRole) {
    msgGenBtn.addEventListener("click", async () => {
      const company = msgCompany.value.trim();
      const role = msgRole.value.trim();

      if (!company || !role) {
        showToast("Please provide Company Name and Target Role.", "warning");
        return;
      }

      msgGenBtn.disabled = true;
      msgGenBtn.textContent = "Writing message...";
      showToast("Generating recruiter message...", "info");

      try {
        const res = await fetch("/api/recruiter-messages/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message_type: msgType.value,
            tone: msgTone.value,
            company_name: company,
            job_title: role,
            recipient_name: msgRecipient.value.trim(),
            additional_notes: msgNotes.value.trim(),
            resume_text: msgResume.value.trim()
          })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          msgSubjectOutput.value = result.data.subject;
          msgBodyOutput.value = result.data.message_body;
          msgModeLabel.textContent = `${result.data.mode_label || 'Generated'} | Scenario: ${result.data.message_type}`;
          msgOutputCard.style.display = "block";
          showToast("Networking message generated!", "success");
          msgOutputCard.scrollIntoView({ behavior: "smooth" });
        } else {
          showToast(result.error || "Failed to generate recruiter message.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error generating message.", "error");
      } finally {
        msgGenBtn.disabled = false;
        msgGenBtn.textContent = "Generate Networking Message";
      }
    });
  }

  if (msgCopyBtn && msgBodyOutput) {
    msgCopyBtn.addEventListener("click", () => {
      const full = `${msgSubjectOutput.value}\n\n${msgBodyOutput.value}`;
      navigator.clipboard.writeText(full)
        .then(() => showToast("Message with subject copied to clipboard!", "success"))
        .catch(() => showToast("Could not access clipboard.", "error"));
    });
  }
});
