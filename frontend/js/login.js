/**
 * Login page logic.
 * - Email tab: ALWAYS goes through OTP (request-otp -> verify-otp). No password path exists.
 * - Mobile tab: phone + OTP via SMS (Twilio on the backend).
 * - Google button: uses Google Identity Services, sends the ID token to /auth/google.
 *
 * On success in any path, tokens + user are stored via API.setTokens/setUser,
 * then we redirect based on role.
 */

// If already logged in, skip straight past the login page.
(function redirectIfLoggedIn() {
  if (API.getUser() && API.getAccessToken()) {
    redirectAfterLogin(API.getUser());
  }
})();

function redirectAfterLogin(user) {
  const destinations = {
    admin: "dashboard.html",
    staff: "dashboard.html",
    kitchen: "kitchen.html",
    customer: "customer-menu.html",
  };
  window.location.href = destinations[user.role] || "dashboard.html";
}

function switchTab(which) {
  document.getElementById("tab-email").classList.toggle("active", which === "email");
  document.getElementById("tab-mobile").classList.toggle("active", which === "mobile");
  document.getElementById("panel-email").classList.toggle("hidden", which !== "email");
  document.getElementById("panel-mobile").classList.toggle("hidden", which !== "mobile");
}

/* ---------------- EMAIL OTP FLOW ---------------- */

async function requestEmailOtp(isResend = false) {
  const emailInput = document.getElementById("email-input");
  const email = (isResend ? document.getElementById("email-display").textContent : emailInput.value).trim();

  if (!email || !email.includes("@")) {
    toast("Enter a valid email address.", "error");
    return;
  }

  const btn = document.getElementById(isResend ? "email-resend-btn" : "email-send-otp-btn");
  btn.disabled = true;
  try {
    await API.auth.requestEmailOtp(email);
    toast(`OTP sent to ${email}`, "success");
    document.getElementById("email-display").textContent = email;
    document.getElementById("email-step-request").classList.add("hidden");
    document.getElementById("email-step-verify").classList.remove("hidden");
    document.getElementById("email-otp-input").focus();
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
  }
}

async function verifyEmailOtp() {
  const email = document.getElementById("email-display").textContent;
  const otp_code = document.getElementById("email-otp-input").value.trim();
  if (otp_code.length !== 6) {
    toast("Enter the 6-digit code.", "error");
    return;
  }

  const btn = document.getElementById("email-verify-btn");
  btn.disabled = true;
  try {
    const data = await API.auth.verifyEmailOtp(email, otp_code);
    API.setTokens(data.access_token, data.refresh_token);
    API.setUser(data.user);
    toast(`Welcome, ${data.user.name}!`, "success");
    redirectAfterLogin(data.user);
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
  }
}

function resetEmailStep() {
  document.getElementById("email-step-verify").classList.add("hidden");
  document.getElementById("email-step-request").classList.remove("hidden");
  document.getElementById("email-otp-input").value = "";
}

/* ---------------- MOBILE OTP FLOW ---------------- */

async function requestMobileOtp(isResend = false) {
  const mobileInput = document.getElementById("mobile-input");
  const phone = (isResend ? document.getElementById("mobile-display").textContent : mobileInput.value).trim();

  if (!phone.startsWith("+") || phone.length < 8) {
    toast("Enter your number with country code, e.g. +919876543210.", "error");
    return;
  }

  const btn = document.getElementById(isResend ? "mobile-resend-btn" : "mobile-send-otp-btn");
  btn.disabled = true;
  try {
    await API.auth.requestMobileOtp(phone);
    toast(`OTP sent to ${phone}`, "success");
    document.getElementById("mobile-display").textContent = phone;
    document.getElementById("mobile-step-request").classList.add("hidden");
    document.getElementById("mobile-step-verify").classList.remove("hidden");
    document.getElementById("mobile-otp-input").focus();
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
  }
}

async function verifyMobileOtp() {
  const phone = document.getElementById("mobile-display").textContent;
  const otp_code = document.getElementById("mobile-otp-input").value.trim();
  if (otp_code.length !== 6) {
    toast("Enter the 6-digit code.", "error");
    return;
  }

  const btn = document.getElementById("mobile-verify-btn");
  btn.disabled = true;
  try {
    const data = await API.auth.verifyMobileOtp(phone, otp_code);
    API.setTokens(data.access_token, data.refresh_token);
    API.setUser(data.user);
    toast(`Welcome, ${data.user.name}!`, "success");
    redirectAfterLogin(data.user);
  } catch (err) {
    toast(err.message, "error");
  } finally {
    btn.disabled = false;
  }
}

function resetMobileStep() {
  document.getElementById("mobile-step-verify").classList.add("hidden");
  document.getElementById("mobile-step-request").classList.remove("hidden");
  document.getElementById("mobile-otp-input").value = "";
}

/* ---------------- GOOGLE LOGIN ---------------- */

// Replace with your real Google OAuth Client ID (must match backend's GOOGLE_CLIENT_ID).
const GOOGLE_CLIENT_ID = "791809735471-3rsh5bmidj6om62jk4h2g53guu183nlf.apps.googleusercontent.com";

window.onload = function initGoogleButton() {
  if (!window.google || !GOOGLE_CLIENT_ID.includes(".apps.googleusercontent.com")) return;
  google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleGoogleCredential,
  });
  google.accounts.id.renderButton(document.getElementById("google-signin-button"), {
    theme: "outline",
    size: "large",
    width: 340,
    text: "continue_with",
  });
};

async function handleGoogleCredential(response) {
  try {
    const data = await API.auth.googleLogin(response.credential);
    API.setTokens(data.access_token, data.refresh_token);
    API.setUser(data.user);
    toast(`Welcome, ${data.user.name}!`, "success");
    redirectAfterLogin(data.user);
  } catch (err) {
    toast(err.message, "error");
  }
}

/* Allow Enter key to submit the active step */
document.addEventListener("keydown", (e) => {
  if (e.key !== "Enter") return;
  if (!document.getElementById("panel-email").classList.contains("hidden")) {
    if (!document.getElementById("email-step-request").classList.contains("hidden")) requestEmailOtp();
    else verifyEmailOtp();
  } else {
    if (!document.getElementById("mobile-step-request").classList.contains("hidden")) requestMobileOtp();
    else verifyMobileOtp();
  }
});
