// ==========================================================
// DevBhumi Horizons — Auth Modal (Login / Sign Up)
// ==========================================================

document.addEventListener("DOMContentLoaded", () => {

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? match[2] : null;
  }

  const overlay = document.getElementById("authModalOverlay");
  if (!overlay) return; // partial not included on this page

  const modal = document.getElementById("authModal");
  const closeBtn = document.getElementById("authModalClose");
  const bodyLogin = document.getElementById("authBodyLogin");
  const bodySignup = document.getElementById("authBodySignup");
  const bodyOtp = document.getElementById("authBodyOtp");
  const showSignupBtn = document.getElementById("showSignupBtn");
  const showLoginBtn = document.getElementById("showLoginBtn");
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  const otpForm = document.getElementById("otpForm");
  const otpBoxes = Array.from(document.querySelectorAll(".otp-box"));
  const otpEmailDisplay = document.getElementById("otpEmailDisplay");
  const otpError = document.getElementById("otpError");
  const resendOtpBtn = document.getElementById("resendOtpBtn");

  let pendingEmail = "";
  let resendCooldownTimer = null;

  const openModal = (mode = "login") => {
    switchTo(mode);
    overlay.classList.add("open");
    document.body.classList.add("auth-modal-open");
  };

  const closeModal = () => {
    overlay.classList.remove("open");
    document.body.classList.remove("auth-modal-open");
  };

  const switchTo = (mode) => {
    bodyLogin.hidden = mode !== "login";
    bodySignup.hidden = mode !== "signup";
    bodyOtp.hidden = mode !== "otp";
  };

  const showOtpPane = (email) => {
    pendingEmail = email;
    otpEmailDisplay.textContent = email;
    otpError.hidden = true;
    otpBoxes.forEach(box => (box.value = ""));
    switchTo("otp");
    otpBoxes[0].focus();
    startResendCooldown();
  };

  const startResendCooldown = (seconds = 30) => {
    let remaining = seconds;
    resendOtpBtn.disabled = true;
    resendOtpBtn.textContent = `Resend OTP (${remaining}s)`;
    clearInterval(resendCooldownTimer);
    resendCooldownTimer = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(resendCooldownTimer);
        resendOtpBtn.disabled = false;
        resendOtpBtn.textContent = "Resend OTP";
      } else {
        resendOtpBtn.textContent = `Resend OTP (${remaining}s)`;
      }
    }, 1000);
  };

  // Open triggers — any element with data-auth-trigger="login" / "signup"
  document.querySelectorAll("[data-auth-trigger]").forEach(trigger => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      openModal(trigger.dataset.authTrigger || "login");
    });
  });

  // Close interactions
  closeBtn.addEventListener("click", closeModal);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("open")) closeModal();
  });

  // Switch between login / signup panes
  showSignupBtn && showSignupBtn.addEventListener("click", () => switchTo("signup"));
  showLoginBtn && showLoginBtn.addEventListener("click", () => switchTo("login"));

  // Show/hide password
  document.querySelectorAll(".auth-toggle-pass").forEach(btn => {
    btn.addEventListener("click", () => {
      const input = document.getElementById(btn.dataset.target);
      if (!input) return;
      const icon = btn.querySelector("i");
      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      icon.classList.toggle("fa-eye-slash", !isHidden);
      icon.classList.toggle("fa-eye", isHidden);
    });
  });

  // ---- Form submits ----
  // TODO: point these at your real Django auth endpoints
  // (e.g. {% url 'login' %} / {% url 'signup' %}) once they exist —
  // for now they're intercepted so the modal doesn't just hard-navigate.
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const email = loginForm.email.value.trim();
      const password = loginForm.password.value;

      fetch("/travel/auth/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ email, password }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            if (data.needs_otp) {
              showOtpPane(data.email);
              return;
            }
            alert(data.error || "Something went wrong.");
            return;
          }
          window.location.reload(); // logged in — refresh so navbar shows logged-in state
        })
        .catch(() => alert("Network error. Please try again."));
    });
  }

  if (signupForm) {
    signupForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const firstName = signupForm.firstName.value.trim();
      const lastName = signupForm.lastName.value.trim();
      const email = signupForm.email.value.trim();
      const password = signupForm.password.value;
      const confirmPassword = signupForm.confirmPassword.value;

      if (password !== confirmPassword) {
        alert("Passwords do not match.");
        return;
      }

      fetch("/travel/auth/signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ firstName, lastName, email, password, confirmPassword }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            alert(data.error || "Something went wrong.");
            return;
          }
          showOtpPane(data.email);
        })
        .catch(() => alert("Network error. Please try again."));
    });
  }

  // ---- OTP boxes: auto-advance, backspace, paste ----
  otpBoxes.forEach((box, i) => {
    box.addEventListener("input", () => {
      box.value = box.value.replace(/[^0-9]/g, "").slice(0, 1);
      if (box.value && otpBoxes[i + 1]) otpBoxes[i + 1].focus();
    });

    box.addEventListener("keydown", (e) => {
      if (e.key === "Backspace" && !box.value && otpBoxes[i - 1]) {
        otpBoxes[i - 1].focus();
      }
    });

    box.addEventListener("paste", (e) => {
      e.preventDefault();
      const digits = (e.clipboardData.getData("text") || "").replace(/[^0-9]/g, "").split("");
      otpBoxes.forEach((b, j) => (b.value = digits[j] || ""));
      const nextEmpty = otpBoxes.findIndex(b => !b.value);
      (nextEmpty === -1 ? otpBoxes[otpBoxes.length - 1] : otpBoxes[nextEmpty]).focus();
    });
  });

  // ---- OTP verify ----
  if (otpForm) {
    otpForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const otp = otpBoxes.map(b => b.value).join("");
      otpError.hidden = true;

      if (otp.length !== 6) {
        otpError.textContent = "Please enter all 6 digits.";
        otpError.hidden = false;
        return;
      }

      fetch("/travel/auth/verify-otp/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ email: pendingEmail, otp }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            otpError.textContent = data.error || "Incorrect OTP.";
            otpError.hidden = false;
            return;
          }
          window.location.reload(); // verified + auto-logged-in on the backend
        })
        .catch(() => {
          otpError.textContent = "Network error. Please try again.";
          otpError.hidden = false;
        });
    });
  }

  // ---- Resend OTP ----
  if (resendOtpBtn) {
    resendOtpBtn.addEventListener("click", () => {
      fetch("/travel/auth/resend-otp/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ email: pendingEmail }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            otpError.textContent = data.error || "Could not resend OTP.";
            otpError.hidden = false;
            return;
          }
          startResendCooldown();
        })
        .catch(() => {
          otpError.textContent = "Network error. Please try again.";
          otpError.hidden = false;
        });
    });
  }

  // ---- Profile dropdown (logged-in nav) ----
  const profileItem = document.querySelector(".nav-profile-item");
  const profileTrigger = document.getElementById("navProfileTrigger");
  const logoutBtn = document.getElementById("navLogoutBtn");

  if (profileItem && profileTrigger) {
    profileTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      profileItem.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
      if (!profileItem.contains(e.target)) profileItem.classList.remove("open");
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") profileItem.classList.remove("open");
    });
  }
  
  // Any logout link/button on the page — navbar dropdown AND profile-page sidebar
  document.querySelectorAll(".js-logout-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      fetch("/travel/auth/logout/", {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
      })
        .then(() => window.location.reload())
        .catch(() => alert("Network error. Please try again."));
    });
  });
  

 // ---- Continue with Google ----
  let googleTokenClient = null;
 
  function initGoogleClient() {
    if (googleTokenClient || !window.google || !window.google.accounts || !window.GOOGLE_CLIENT_ID) return;
 
    googleTokenClient = google.accounts.oauth2.initTokenClient({
      client_id: window.GOOGLE_CLIENT_ID,
      scope: "email profile",
      callback: (tokenResponse) => {
        if (!tokenResponse || !tokenResponse.access_token) return;
 
        fetch("/travel/auth/google/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ access_token: tokenResponse.access_token }),
        })
          .then(res => res.json())
          .then(data => {
            if (!data.success) {
              alert(data.error || "Google sign-in failed.");
              return;
            }
            window.location.reload();
          })
          .catch(() => alert("Network error. Please try again."));
      },
    });
  }
 
  // the GIS script loads async — try once now, and once more on window load in case it's slow
  initGoogleClient();
  window.addEventListener("load", initGoogleClient);
 
  document.querySelectorAll(".auth-google-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (!googleTokenClient) {
        initGoogleClient();
        if (!googleTokenClient) {
          alert("Google sign-in is still loading — please try again in a moment.");
          return;
        }
      }
      googleTokenClient.requestAccessToken();
    });
  });

});