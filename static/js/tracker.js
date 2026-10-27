/**
 * SQLite Application Tracker Client Logic.
 * Full CRUD: Fetch, Search, Filter, Create, Edit, Delete with modal confirmation.
 */

document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("applicationsTableBody");
  const searchInput = document.getElementById("trackerSearchInput");
  const statusFilter = document.getElementById("trackerStatusFilter");
  const resetBtn = document.getElementById("resetFilterBtn");

  // Modal Elements
  const modalOverlay = document.getElementById("appModalOverlay");
  const openAddBtn = document.getElementById("openAddModalBtn");
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const modalCancelBtn = document.getElementById("modalCancelBtn");
  const modalSaveBtn = document.getElementById("modalSaveBtn");
  const modalTitle = document.getElementById("modalTitle");

  // Form Fields
  const modalAppId = document.getElementById("modalAppId");
  const modalCompany = document.getElementById("modalCompany");
  const modalRole = document.getElementById("modalRole");
  const modalDate = document.getElementById("modalDate");
  const modalStatus = document.getElementById("modalStatus");
  const modalLink = document.getElementById("modalLink");
  const modalNotes = document.getElementById("modalNotes");

  // Delete Modal Elements
  const deleteOverlay = document.getElementById("deleteModalOverlay");
  const deleteTargetName = document.getElementById("deleteTargetName");
  const deleteConfirmBtn = document.getElementById("deleteConfirmBtn");
  const deleteCancelBtn = document.getElementById("deleteCancelBtn");
  const deleteCloseBtn = document.getElementById("deleteModalCloseBtn");

  let pendingDeleteId = null;

  // Initial load
  loadApplications();

  // Search & Filter listeners
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => loadApplications(), 300);
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", () => loadApplications());
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      searchInput.value = "";
      statusFilter.value = "";
      loadApplications();
    });
  }

  // Open Add Modal
  if (openAddBtn) {
    openAddBtn.addEventListener("click", () => {
      modalTitle.textContent = "Add Job Application";
      modalAppId.value = "";
      modalCompany.value = "";
      modalRole.value = "";
      // Set today's date by default
      const today = new Date().toISOString().split("T")[0];
      modalDate.value = today;
      modalStatus.value = "Applied";
      modalLink.value = "";
      modalNotes.value = "";
      modalOverlay.classList.add("active");
    });
  }

  // Close Add/Edit Modal
  function closeModal() {
    modalOverlay.classList.remove("active");
  }
  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (modalCancelBtn) modalCancelBtn.addEventListener("click", closeModal);

  // Close Delete Modal
  function closeDeleteModal() {
    deleteOverlay.classList.remove("active");
    pendingDeleteId = null;
  }
  if (deleteCloseBtn) deleteCloseBtn.addEventListener("click", closeDeleteModal);
  if (deleteCancelBtn) deleteCancelBtn.addEventListener("click", closeDeleteModal);

  // Save Application (Create or Update)
  if (modalSaveBtn) {
    modalSaveBtn.addEventListener("click", async () => {
      const company = modalCompany.value.trim();
      const role = modalRole.value.trim();
      const appDate = modalDate.value.trim();
      const status = modalStatus.value;
      const link = modalLink.value.trim();
      const notes = modalNotes.value.trim();
      const appId = modalAppId.value;

      if (!company || !role || !appDate) {
        showToast("Company, Role, and Date are required.", "warning");
        return;
      }

      modalSaveBtn.disabled = true;
      modalSaveBtn.textContent = "Saving...";

      try {
        const url = appId ? `/api/applications/${appId}` : "/api/applications";
        const method = appId ? "PUT" : "POST";

        const res = await fetch(url, {
          method: method,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            company: company,
            role: role,
            application_date: appDate,
            status: status,
            job_link: link,
            notes: notes
          })
        });

        const result = await res.json();
        if (res.ok && result.success) {
          showToast(appId ? "Application updated!" : "Application added to SQLite!", "success");
          closeModal();
          loadApplications();
          refreshStats();
        } else {
          showToast(result.error || "Failed to save application.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error saving application.", "error");
      } finally {
        modalSaveBtn.disabled = false;
        modalSaveBtn.textContent = "Save Application";
      }
    });
  }

  // Confirm Delete
  if (deleteConfirmBtn) {
    deleteConfirmBtn.addEventListener("click", async () => {
      if (!pendingDeleteId) return;

      deleteConfirmBtn.disabled = true;
      try {
        const res = await fetch(`/api/applications/${pendingDeleteId}`, {
          method: "DELETE"
        });
        const result = await res.json();

        if (res.ok && result.success) {
          showToast("Application deleted permanently.", "success");
          closeDeleteModal();
          loadApplications();
          refreshStats();
        } else {
          showToast(result.error || "Failed to delete application.", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Network error deleting application.", "error");
      } finally {
        deleteConfirmBtn.disabled = false;
      }
    });
  }

  // Load applications from API
  async function loadApplications() {
    if (!tableBody) return;

    const query = searchInput ? searchInput.value.trim() : "";
    const status = statusFilter ? statusFilter.value.trim() : "";

    let url = "/api/applications?";
    if (query) url += `search=${encodeURIComponent(query)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;

    try {
      const res = await fetch(url);
      const data = await res.json();

      if (res.ok && data.success) {
        renderTable(data.applications || []);
      } else {
        tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #DC2626; padding: 20px;">${data.error || "Error loading applications."}</td></tr>`;
      }
    } catch (err) {
      console.error(err);
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: #DC2626; padding: 20px;">Could not connect to backend database.</td></tr>`;
    }
  }

  // Render Table Rows
  function renderTable(apps) {
    tableBody.innerHTML = "";

    if (apps.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 36px;">No applications match your search or filter.</td></tr>`;
      return;
    }

    apps.forEach((app) => {
      const tr = document.createElement("tr");

      const linkHtml = app.job_link
        ? `<a href="${app.job_link}" target="_blank" rel="noopener noreferrer" style="color: var(--blue-primary); text-decoration: none; font-size: 0.8rem;">View Link ↗</a>`
        : `<span style="color: var(--text-muted); font-size: 0.8rem;">None</span>`;

      const notesHtml = app.notes
        ? `<span title="${app.notes}" style="font-size: 0.82rem; color: var(--text-secondary); display: inline-block; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${app.notes}</span>`
        : `<span style="color: var(--text-muted); font-size: 0.8rem;">-</span>`;

      tr.innerHTML = `
        <td><strong>${app.company}</strong></td>
        <td>${app.role}</td>
        <td>${app.application_date}</td>
        <td><span class="status-badge ${app.status}">${app.status}</span></td>
        <td>${linkHtml}</td>
        <td>${notesHtml}</td>
        <td style="text-align: right; white-space: nowrap;">
          <button class="btn btn-secondary btn-sm edit-app-btn" data-id="${app.id}" style="margin-right: 6px;">✏️ Edit</button>
          <button class="btn btn-danger btn-sm delete-app-btn" data-id="${app.id}" data-name="${app.company} - ${app.role}">🗑️ Delete</button>
        </td>
      `;

      tableBody.appendChild(tr);
    });

    // Attach edit listeners
    document.querySelectorAll(".edit-app-btn").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const id = e.currentTarget.dataset.id;
        try {
          const res = await fetch(`/api/applications/${id}`);
          const data = await res.json();
          if (res.ok && data.success) {
            const a = data.application;
            modalTitle.textContent = "Edit Job Application";
            modalAppId.value = a.id;
            modalCompany.value = a.company;
            modalRole.value = a.role;
            modalDate.value = a.application_date;
            modalStatus.value = a.status;
            modalLink.value = a.job_link || "";
            modalNotes.value = a.notes || "";
            modalOverlay.classList.add("active");
          }
        } catch (err) {
          showToast("Error loading application details.", "error");
        }
      });
    });

    // Attach delete listeners
    document.querySelectorAll(".delete-app-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        pendingDeleteId = e.currentTarget.dataset.id;
        deleteTargetName.textContent = e.currentTarget.dataset.name;
        deleteOverlay.classList.add("active");
      });
    });
  }

  // Refresh Top Stat Cards
  async function refreshStats() {
    try {
      const res = await fetch("/api/dashboard/stats");
      const data = await res.json();
      if (res.ok && data.success && data.stats) {
        const s = data.stats;
        const totalElem = document.getElementById("trackerTotal");
        const assElem = document.getElementById("trackerAssessment");
        const intElem = document.getElementById("trackerInterview");
        const offElem = document.getElementById("trackerOffer");

        if (totalElem) totalElem.textContent = s.total_applications;
        if (assElem) assElem.textContent = s.assessment;
        if (intElem) intElem.textContent = s.interviews;
        if (offElem) offElem.textContent = s.offers;
      }
    } catch (err) {
      console.warn("Could not refresh tracker stats:", err);
    }
  }
});
