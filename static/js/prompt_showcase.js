/**
 * Prompt Engineering Showcase & Live Production Prompt Inspector Client Logic.
 */

document.addEventListener("DOMContentLoaded", () => {
  const tabBtns = document.querySelectorAll(".prompt-tab-btn");
  const tabContents = document.querySelectorAll(".prompt-tab-content");
  const liveSelect = document.getElementById("liveTemplateSelect");
  const liveCode = document.getElementById("liveTemplateCode");
  const refreshBtn = document.getElementById("refreshLivePromptsBtn");

  let livePromptsData = null;

  // Tab switching
  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.target;

      tabBtns.forEach((b) => {
        b.classList.remove("btn-primary", "active");
        b.classList.add("btn-secondary");
      });
      btn.classList.remove("btn-secondary");
      btn.classList.add("btn-primary", "active");

      tabContents.forEach((tc) => {
        tc.style.display = tc.id === targetId ? "block" : "none";
      });

      // If switching to live inspector, fetch live prompts
      if (targetId === "tab-live-inspector" && !livePromptsData) {
        fetchLivePrompts();
      }
    });
  });

  // Fetch live prompt templates from memory
  async function fetchLivePrompts() {
    if (!liveCode) return;
    liveCode.textContent = "Fetching in-memory production prompt templates from services/prompt_templates.py...";

    try {
      const res = await fetch("/api/prompts/live");
      const data = await res.json();

      if (res.ok && data.success) {
        livePromptsData = data;
        const sysElem = document.getElementById("liveSystemPrompt");
        if (sysElem) sysElem.textContent = data.system_prompt;

        updateSelectedTemplate();
        showToast("Live production prompts loaded!", "success");
      } else {
        liveCode.textContent = "Failed to load live prompts from backend.";
      }
    } catch (err) {
      console.error(err);
      liveCode.textContent = "Network error connecting to prompt API.";
    }
  }

  function updateSelectedTemplate() {
    if (!livePromptsData || !liveSelect || !liveCode) return;
    const key = liveSelect.value;
    const template = livePromptsData.templates[key] || "Template not found.";
    liveCode.textContent = template;
  }

  if (liveSelect) {
    liveSelect.addEventListener("change", updateSelectedTemplate);
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      livePromptsData = null;
      fetchLivePrompts();
    });
  }
});
