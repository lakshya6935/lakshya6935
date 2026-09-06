/* ===========================================================
   StayLuxe — Shared frontend utilities
   Used by customer, admin and owner interfaces alike.
   =========================================================== */
const API_BASE_URL = "https://hotel-management-system-jssb.onrender.com/api";

/* ---------- Toast notifications ---------- */
function ensureToastContainer() {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  return container;
}

function showToast(message, type = "info", duration = 3500) {
  const container = ensureToastContainer();
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "slideIn .3s ease reverse";
    setTimeout(() => toast.remove(), 280);
  }, duration);
}

/* ---------- Auth/local storage helpers ---------- */
function saveSession(token, user) {
  localStorage.setItem("stayluxe_token", token);
  localStorage.setItem("stayluxe_user", JSON.stringify(user));
}

function getToken() {
  return localStorage.getItem("stayluxe_token");
}

function getCurrentUser() {
  const raw = localStorage.getItem("stayluxe_user");
  return raw ? JSON.parse(raw) : null;
}

function logout(redirectUrl = "login.html") {
  localStorage.removeItem("stayluxe_token");
  localStorage.removeItem("stayluxe_user");
  window.location.href = redirectUrl;
}

function requireRole(expectedRole, loginPage) {
  const user = getCurrentUser();
  const token = getToken();
  if (!user || !token || user.role !== expectedRole) {
    window.location.href = loginPage;
  }
  return user;
}

/* ---------- API request wrapper ---------- */
async function apiRequest(path, { method = "GET", body = null, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });
    const data = await response.json().catch(() => ({}));

    if (response.status === 401 && auth) {
      showToast(data.message || "Session expired, please log in again.", "error");
      setTimeout(() => logout(), 1200);
    }

    return { ok: response.ok, status: response.status, data };
  } catch (err) {
    return {
      ok: false,
      status: 0,
      data: { success: false, message: "Cannot reach server. Is the backend running on port 5000?" },
    };
  }
}

/* ---------- Currency formatting (INR) ---------- */
function formatINR(amount) {
  const num = Number(amount) || 0;
  return "₹" + num.toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

/* ---------- Simple modal helper ---------- */
function openModal(innerHtml, onMount) {
  closeModal();
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.id = "activeModal";
  overlay.innerHTML = `<div class="modal-box">
      <button class="modal-close" onclick="closeModal()">&times;</button>
      ${innerHtml}
    </div>`;
  overlay.addEventListener("click", (e) => { if (e.target === overlay) closeModal(); });
  document.body.appendChild(overlay);
  if (typeof onMount === "function") onMount(overlay);
}

function closeModal() {
  const existing = document.getElementById("activeModal");
  if (existing) existing.remove();
}

/* ---------- Scroll reveal animation ---------- */
function initScrollReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add("in-view");
    });
  }, { threshold: 0.15 });
  items.forEach((item) => observer.observe(item));
}

document.addEventListener("DOMContentLoaded", initScrollReveal);

/* ---------- Mobile nav toggle (used across all interfaces) ---------- */
function initNavToggle() {
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
  }
}
document.addEventListener("DOMContentLoaded", initNavToggle);
