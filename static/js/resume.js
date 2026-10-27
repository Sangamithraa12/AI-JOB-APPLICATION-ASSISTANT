/**
 * Resume upload, drag-and-drop, text extraction, and privacy handling.
 */

document.addEventListener("DOMContentLoaded", () => {
  const dropzone = document.getElementById("resumeDropzone");
  const fileInput = document.getElementById("resumeFileInput");
  const resultCard = document.getElementById("extractionResultCard");
  const textarea = document.getElementById("extractedResumeTextarea");
  const metaText = document.getElementById("resumeMetaText");
  const charSpan = document.getElementById("charCountSpan");
  const wordSpan = document.getElementById("wordCountSpan");
  const copyBtn = document.getElementById("copyResumeTextBtn");
  const matcherBtn = document.getElementById("useInMatcherBtn");
  const scannedBanner = document.getElementById("scannedWarningBanner");
  const scannedMsg = document.getElementById("scannedWarningMessage");

  if (!dropzone || !fileInput) return;

  // Open file selector on click
  dropzone.addEventListener("click", () => fileInput.click());

  // Drag and drop handlers
  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleFileUpload(fileInput.files[0]);
    }
  });

  // Handle PDF upload and extraction
  async function handleFileUpload(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      showToast("Invalid file format. Please upload a PDF (.pdf) file.", "error");
      return;
    }

    const maxBytes = 5 * 1024 * 1024; // 5 MB
    if (file.size > maxBytes) {
      showToast("File exceeds maximum 5MB size limit.", "error");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    dropzone.style.opacity = "0.5";
    dropzone.querySelector(".dropzone-title").textContent = "Extracting text using pypdf...";
    showToast("Extracting resume content...", "info");

    try {
      const response = await fetch("/api/resume/upload", {
        method: "POST",
        body: formData
      });

      const result = await response.json();

      if (response.ok && result.success) {
        showToast("Resume extracted successfully!", "success");
        resultCard.style.display = "block";
        textarea.value = result.extracted_text;

        const meta = result.metadata || {};
        metaText.textContent = `Extracted from ${result.filename} (${meta.num_pages || 1} pages, ${meta.word_count || 0} words).`;
        charSpan.textContent = meta.char_count || result.extracted_text.length;
        wordSpan.textContent = meta.word_count || (result.extracted_text.split(/\s+/).filter(Boolean).length);

        // Check for scanned / image-only warning
        if (meta.is_scanned_or_empty) {
          scannedBanner.style.display = "flex";
          scannedMsg.textContent = meta.warning || "Warning: Minimal text extracted. This PDF may be a scanned image.";
        } else {
          scannedBanner.style.display = "none";
        }

        // Cache locally for smooth cross-page workflow
        localStorage.setItem("shared_resume_text", result.extracted_text);

        // Scroll to result
        resultCard.scrollIntoView({ behavior: "smooth" });
      } else {
        showToast(result.error || "Failed to extract resume.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("Network or server error during upload.", "error");
    } finally {
      dropzone.style.opacity = "1";
      dropzone.querySelector(".dropzone-title").textContent = "Click to upload or drag & drop your resume PDF";
      fileInput.value = "";
    }
  }

  // Update counters on manual edit
  if (textarea) {
    textarea.addEventListener("input", () => {
      const val = textarea.value;
      charSpan.textContent = val.length;
      wordSpan.textContent = val.split(/\s+/).filter(Boolean).length;
      localStorage.setItem("shared_resume_text", val);
    });
  }

  // Copy text button
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      if (!textarea.value.trim()) return;
      navigator.clipboard.writeText(textarea.value)
        .then(() => showToast("Extracted resume text copied to clipboard!", "success"))
        .catch(() => showToast("Could not access clipboard.", "error"));
    });
  }

  // Send to Matcher button
  if (matcherBtn) {
    matcherBtn.addEventListener("click", () => {
      if (!textarea.value.trim()) {
        showToast("Please extract or enter resume text first.", "warning");
        return;
      }
      localStorage.setItem("shared_resume_text", textarea.value.trim());
      window.location.href = "/matching";
    });
  }

  // Restore cached resume text if available
  const cached = localStorage.getItem("shared_resume_text");
  if (cached && textarea && !textarea.value) {
    textarea.value = cached;
    charSpan.textContent = cached.length;
    wordSpan.textContent = cached.split(/\s+/).filter(Boolean).length;
    resultCard.style.display = "block";
    metaText.textContent = "Loaded previously extracted resume from local session.";
  }
});
