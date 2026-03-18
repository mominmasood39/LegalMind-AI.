/**
 * LegalMind-AI — Shared frontend utilities
 */

// Backend API base URL.  Empty string = same origin (when served by FastAPI).
// Override by setting window.LEGALMIND_API in a page-level script.
const API_BASE = window.LEGALMIND_API || "";

/**
 * Escape HTML special characters to prevent XSS when inserting user-provided
 * strings into innerHTML.
 */
function escapeHtml(text) {
  if (typeof text !== "string") return String(text);
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
