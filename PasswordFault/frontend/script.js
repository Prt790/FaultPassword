/**
 * Password Fault Detector — Frontend Client
 * Handles real-time input evaluation, backend API communication,
 * password visibility toggling, and UI state rendering.
 */

// Configuration
const API_BASE_URL = "http://127.0.0.1:5000";
const CHECK_ENDPOINT = `${API_BASE_URL}/check-password`;
const DEBOUNCE_DELAY_MS = 150;

// DOM Elements
const passwordInput = document.getElementById("password-input");
const togglePasswordBtn = document.getElementById("toggle-password-btn");
const iconShow = document.getElementById("icon-show");
const iconHide = document.getElementById("icon-hide");
const charCounter = document.getElementById("char-counter");

const strengthMeter = document.getElementById("strength-meter");
const meterFill = document.getElementById("meter-fill");
const strengthBadge = document.getElementById("strength-badge");
const strengthScore = document.getElementById("strength-score");
const strengthSummary = document.getElementById("strength-summary");

const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");

// Debounce timer and controller for aborting obsolete fetch requests
let debounceTimer = null;
let activeAbortController = null;
let isBackendOnline = false;

// Special characters for fallback client-side check if backend is offline
const SPECIAL_CHARS = new Set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~");

/**
 * Initialize application events and check backend health on load.
 */
document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  checkBackendHealth();
  resetUI();
});

/**
 * Attach user interaction listeners.
 */
function setupEventListeners() {
  // Real-time password typing
  passwordInput.addEventListener("input", onPasswordInput);

  // Show/Hide password toggle
  togglePasswordBtn.addEventListener("click", togglePasswordVisibility);
}

/**
 * Toggles input type between password and text.
 */
function togglePasswordVisibility() {
  const isPassword = passwordInput.getAttribute("type") === "password";

  if (isPassword) {
    passwordInput.setAttribute("type", "text");
    iconShow.classList.add("hidden");
    iconHide.classList.remove("hidden");
    togglePasswordBtn.setAttribute("aria-label", "Hide password");
    togglePasswordBtn.setAttribute("title", "Hide password");
  } else {
    passwordInput.setAttribute("type", "password");
    iconShow.classList.remove("hidden");
    iconHide.classList.add("hidden");
    togglePasswordBtn.setAttribute("aria-label", "Show password as plain text");
    togglePasswordBtn.setAttribute("title", "Show password as plain text");
  }

  // Refocus input for seamless typing experience
  passwordInput.focus();
}

/**
 * Handles typing events with light debouncing to avoid API flooding.
 */
function onPasswordInput() {
  const password = passwordInput.value;

  // Immediate character counter update
  const length = password.length;
  charCounter.textContent = `${length} character${length === 1 ? "" : "s"}`;

  if (length === 0) {
    resetUI();
    return;
  }

  // Clear pending debounce
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    evaluatePassword(password);
  }, DEBOUNCE_DELAY_MS);
}

/**
 * Sends the password to the Flask backend API for evaluation.
 * If backend is unreachable, gracefully falls back to client evaluation.
 */
async function evaluatePassword(password) {
  // Abort previous in-flight request if user kept typing
  if (activeAbortController) {
    activeAbortController.abort();
  }
  activeAbortController = new AbortController();

  try {
    const response = await fetch(CHECK_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ password }),
      signal: activeAbortController.signal,
    });

    if (!response.ok) {
      throw new Error(`Server returned HTTP ${response.status}`);
    }

    const data = await response.json();
    setServerStatus(true, "Connected to backend API");
    renderResults(data, password.length > 0);
  } catch (err) {
    if (err.name === "AbortError") {
      // Ignored: request was superseded by a newer keystroke
      return;
    }

    // Backend is offline or unreachable - use client fallback so user isn't blocked
    setServerStatus(
      false,
      "Backend offline — Run `python backend/app.py` (using local fallback)"
    );
    const fallbackData = evaluateLocally(password);
    renderResults(fallbackData, password.length > 0);
  }
}

/**
 * Checks if backend server is running.
 */
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/`, { method: "GET" });
    if (res.ok) {
      setServerStatus(true, "Connected to backend API (http://127.0.0.1:5000)");
      isBackendOnline = true;
    } else {
      setServerStatus(false, "Backend unreachable. Run `python backend/app.py`");
    }
  } catch {
    setServerStatus(false, "Backend unreachable. Run `python backend/app.py`");
  }
}

/**
 * Updates the connection status banner.
 */
function setServerStatus(online, message) {
  if (online) {
    statusDot.className = "status-dot connected";
  } else {
    statusDot.className = "status-dot disconnected";
  }
  statusText.textContent = message;
}

/**
 * Fallback password evaluator matching the backend specification.
 */
function evaluateLocally(password) {
  const hasMinLength = password.length >= 8;
  const hasLowercase = /[a-z]/.test(password);
  const hasUppercase = /[A-Z]/.test(password);
  const hasDigit = /[0-9]/.test(password);
  const hasSpecial = [...password].some((ch) => SPECIAL_CHARS.has(ch));

  const requirements = [
    { id: "min_length", label: "Minimum 8 characters", met: hasMinLength },
    { id: "lowercase", label: "At least one lowercase letter (a–z)", met: hasLowercase },
    { id: "uppercase", label: "At least one uppercase letter (A–Z)", met: hasUppercase },
    { id: "digit", label: "At least one number (0–9)", met: hasDigit },
    { id: "special_char", label: "At least one special character (!@#$%...)", met: hasSpecial },
  ];

  const satisfiedCount = requirements.filter((r) => r.met).length;
  let strength = "Weak";
  if (satisfiedCount >= 5) {
    strength = "Strong";
  } else if (satisfiedCount >= 3) {
    strength = "Medium";
  }

  const missingRequirements = requirements.filter((r) => !r.met).map((r) => r.label);

  return {
    password_length: password.length,
    requirements,
    satisfied_count: satisfiedCount,
    total_requirements: 5,
    strength,
    missing_requirements: missingRequirements,
  };
}

/**
 * Updates DOM checklist, strength meter, and summary labels.
 */
function renderResults(data, hasInput) {
  const { requirements, satisfied_count, strength, missing_requirements } = data;

  // 1. Update each requirement item in the checklist
  requirements.forEach((req) => {
    const itemEl = document.getElementById(`req-${req.id}`);
    if (!itemEl) return;

    const iconIndicator = itemEl.querySelector(".icon-indicator");

    if (req.met) {
      itemEl.className = "req-item is-met";
      iconIndicator.className = "icon-indicator icon-check";
      iconIndicator.textContent = "✓";
      itemEl.setAttribute("aria-checked", "true");
    } else {
      itemEl.className = hasInput ? "req-item is-missing" : "req-item";
      iconIndicator.className = "icon-indicator icon-cross";
      iconIndicator.textContent = "✕";
      itemEl.setAttribute("aria-checked", "false");
    }
  });

  // 2. Update Strength Bar & Accessibility
  const percentage = Math.round((satisfied_count / 5) * 100);
  meterFill.style.width = `${percentage}%`;
  strengthMeter.setAttribute("aria-valuenow", satisfied_count);
  strengthMeter.setAttribute("aria-valuetext", `${strength} (${satisfied_count} of 5 satisfied)`);

  // Clear previous fill classes
  meterFill.className = "meter-fill";
  strengthBadge.className = "strength-badge";

  if (!hasInput || satisfied_count === 0) {
    meterFill.style.width = "0%";
    strengthBadge.textContent = "None";
    strengthBadge.classList.add("badge-empty");
  } else if (strength === "Weak") {
    meterFill.classList.add("fill-weak");
    strengthBadge.textContent = "Weak";
    strengthBadge.classList.add("badge-weak");
  } else if (strength === "Medium") {
    meterFill.classList.add("fill-medium");
    strengthBadge.textContent = "Medium";
    strengthBadge.classList.add("badge-medium");
  } else if (strength === "Strong") {
    meterFill.classList.add("fill-strong");
    strengthBadge.textContent = "Strong";
    strengthBadge.classList.add("badge-strong");
  }

  // 3. Update Text Scores and Guidance
  strengthScore.textContent = `${satisfied_count} of 5 requirements met`;

  if (!hasInput) {
    strengthSummary.textContent = "Start typing above";
  } else if (satisfied_count === 5) {
    strengthSummary.textContent = "🎉 All requirements satisfied!";
  } else {
    strengthSummary.textContent = `Missing: ${missing_requirements.length} requirement${
      missing_requirements.length === 1 ? "" : "s"
    }`;
  }
}

/**
 * Resets the UI to initial empty state.
 */
function resetUI() {
  charCounter.textContent = "0 characters";
  meterFill.style.width = "0%";
  meterFill.className = "meter-fill";

  strengthBadge.textContent = "None";
  strengthBadge.className = "strength-badge badge-empty";

  strengthScore.textContent = "0 of 5 requirements met";
  strengthSummary.textContent = "Start typing above";

  strengthMeter.setAttribute("aria-valuenow", "0");
  strengthMeter.setAttribute("aria-valuetext", "No password entered");

  const items = document.querySelectorAll(".req-item");
  items.forEach((item) => {
    item.className = "req-item";
    const icon = item.querySelector(".icon-indicator");
    if (icon) {
      icon.className = "icon-indicator icon-cross";
      icon.textContent = "✕";
    }
    item.setAttribute("aria-checked", "false");
  });
}
