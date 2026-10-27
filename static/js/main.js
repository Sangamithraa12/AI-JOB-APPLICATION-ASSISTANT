/**
 * Main application JavaScript: Toast notifications, mobile nav, and API helpers.
 */

// Global Toast Notification Helper
function showToast(message, type = "info", duration = 3500) {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;

  let icon = "ℹ️";
  if (type === "success") icon = "✅";
  if (type === "error") icon = "❌";
  if (type === "warning") icon = "⚠️";

  toast.innerHTML = `<span>${icon}</span><div style="flex: 1;">${message}</div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Mobile Sidebar Toggle
document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("mobileMenuToggle");
  const sidebar = document.getElementById("appSidebar");

  if (menuBtn && sidebar) {
    menuBtn.addEventListener("click", () => {
      sidebar.classList.toggle("open");
    });

    // Close sidebar on click outside on mobile
    document.addEventListener("click", (e) => {
      if (window.innerWidth <= 992 && !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    });
  }

  // Check and refresh AI provider status
  fetchAIStatus();
});

// Fetch current AI status
async function fetchAIStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();
    if (data.success && data.status) {
      const status = data.status;
      const pill = document.getElementById("aiStatusPill");
      const text = document.getElementById("aiStatusText");
      if (pill && text) {
        if (status.is_live_ai) {
          pill.className = "ai-status-pill live";
          text.textContent = `Live AI: ${status.model}`;
        } else {
          pill.className = "ai-status-pill demo";
          text.textContent = "Demo Mode (Rule-Based)";
        }
        pill.title = status.notice;
      }
    }
  } catch (err) {
    console.warn("Could not check AI status:", err);
  }
}
