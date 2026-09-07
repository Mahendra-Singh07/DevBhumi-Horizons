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
  const bodyForgot = document.getElementById("authBodyForgot");
  const bodyResetPassword = document.getElementById("authBodyResetPassword");
  const showSignupBtn = document.getElementById("showSignupBtn");
  const showLoginBtn = document.getElementById("showLoginBtn");
  const showForgotBtn = document.getElementById("showForgotBtn");
  const backToLoginFromForgot = document.getElementById("backToLoginFromForgot");
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  const otpForm = document.getElementById("otpForm");
  const otpBoxes = Array.from(document.querySelectorAll("#authBodyOtp .otp-box"));
  const otpEmailDisplay = document.getElementById("otpEmailDisplay");
  const otpError = document.getElementById("otpError");
  const resendOtpBtn = document.getElementById("resendOtpBtn");

  const forgotForm = document.getElementById("forgotForm");
  const forgotError = document.getElementById("forgotError");
  const resetPasswordForm = document.getElementById("resetPasswordForm");
  const resetOtpBoxes = Array.from(document.querySelectorAll("#resetOtpInputs .otp-box"));
  const resetEmailDisplay = document.getElementById("resetEmailDisplay");
  const resetError = document.getElementById("resetError");
  const resendResetOtpBtn = document.getElementById("resendResetOtpBtn");

  let pendingResetEmail = "";
  let pendingEmail = "";

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
    bodyForgot.hidden = mode !== "forgot";
    bodyResetPassword.hidden = mode !== "reset";
  };

  const showOtpPane = (email) => {
    pendingEmail = email;
    otpEmailDisplay.textContent = email;
    otpError.hidden = true;
    otpBoxes.forEach(box => (box.value = ""));
    switchTo("otp");
    otpBoxes[0].focus();
    startResendCooldown(resendOtpBtn);
  };

  const showResetPane = (email) => {
    pendingResetEmail = email;
    resetEmailDisplay.textContent = email;
    resetError.hidden = true;
    resetOtpBoxes.forEach(box => (box.value = ""));
    document.getElementById("newPassword").value = "";
    document.getElementById("confirmNewPassword").value = "";
    switchTo("reset");
    resetOtpBoxes[0].focus();
    startResendCooldown(resendResetOtpBtn);
  };

  const cooldownTimers = new Map();

  const startResendCooldown = (button, seconds = 30) => {
    let remaining = seconds;
    button.disabled = true;
    button.textContent = `Resend OTP (${remaining}s)`;
    clearInterval(cooldownTimers.get(button));
    const timer = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(cooldownTimers.get(button));
        button.disabled = false;
        button.textContent = "Resend OTP";
      } else {
        button.textContent = `Resend OTP (${remaining}s)`;
      }
    }, 1000);
    cooldownTimers.set(button, timer);
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
  showForgotBtn && showForgotBtn.addEventListener("click", (e) => {
    e.preventDefault();
    forgotError.hidden = true;
    switchTo("forgot");
  });
  backToLoginFromForgot && backToLoginFromForgot.addEventListener("click", () => switchTo("login"));

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

  // ---- OTP boxes: auto-advance, backspace, paste (reusable for any 6-box group) ----
  function wireOtpGroup(boxes) {
    boxes.forEach((box, i) => {
      box.addEventListener("input", () => {
        box.value = box.value.replace(/[^0-9]/g, "").slice(0, 1);
        if (box.value && boxes[i + 1]) boxes[i + 1].focus();
      });

      box.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !box.value && boxes[i - 1]) {
          boxes[i - 1].focus();
        }
      });

      box.addEventListener("paste", (e) => {
        e.preventDefault();
        const digits = (e.clipboardData.getData("text") || "").replace(/[^0-9]/g, "").split("");
        boxes.forEach((b, j) => (b.value = digits[j] || ""));
        const nextEmpty = boxes.findIndex(b => !b.value);
        (nextEmpty === -1 ? boxes[boxes.length - 1] : boxes[nextEmpty]).focus();
      });
    });
  }

  wireOtpGroup(otpBoxes);
  wireOtpGroup(resetOtpBoxes);

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
          startResendCooldown(resendOtpBtn);
        })
        .catch(() => {
          otpError.textContent = "Network error. Please try again.";
          otpError.hidden = false;
        });
    });
  }

  // ---- Forgot password: step 1 — send reset code ----
  if (forgotForm) {
    forgotForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const email = forgotForm.email.value.trim();
      forgotError.hidden = true;

      fetch("/travel/auth/forgot-password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ email }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            forgotError.textContent = data.error || "Something went wrong.";
            forgotError.hidden = false;
            return;
          }
          showResetPane(data.email);
        })
        .catch(() => {
          forgotError.textContent = "Network error. Please try again.";
          forgotError.hidden = false;
        });
    });
  }

  // ---- Forgot password: step 2 — verify code + set new password ----
  if (resetPasswordForm) {
    resetPasswordForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const otp = resetOtpBoxes.map(b => b.value).join("");
      const newPassword = document.getElementById("newPassword").value;
      const confirmNewPassword = document.getElementById("confirmNewPassword").value;
      resetError.hidden = true;

      if (otp.length !== 6) {
        resetError.textContent = "Please enter all 6 digits.";
        resetError.hidden = false;
        return;
      }

      if (newPassword !== confirmNewPassword) {
        resetError.textContent = "Passwords do not match.";
        resetError.hidden = false;
        return;
      }

      fetch("/travel/auth/reset-password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          email: pendingResetEmail,
          otp,
          new_password: newPassword,
          confirm_new_password: confirmNewPassword,
        }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            resetError.textContent = data.error || "Could not reset password.";
            resetError.hidden = false;
            return;
          }
          window.location.reload(); // password reset + auto-logged-in on the backend
        })
        .catch(() => {
          resetError.textContent = "Network error. Please try again.";
          resetError.hidden = false;
        });
    });
  }

  // ---- Forgot password: resend reset code ----
  if (resendResetOtpBtn) {
    resendResetOtpBtn.addEventListener("click", () => {
      fetch("/travel/auth/forgot-password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ email: pendingResetEmail }),
      })
        .then(res => res.json())
        .then(data => {
          if (!data.success) {
            resetError.textContent = data.error || "Could not resend code.";
            resetError.hidden = false;
            return;
          }
          startResendCooldown(resendResetOtpBtn);
        })
        .catch(() => {
          resetError.textContent = "Network error. Please try again.";
          resetError.hidden = false;
        });
    });
  }

  // ---- Profile dropdown (logged-in nav) ----
  const profileItem = document.querySelector(".nav-profile-item");
  const profileTrigger = document.getElementById("navProfileTrigger");

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
        console.log("Google token response:", tokenResponse);

        if (!tokenResponse || !tokenResponse.access_token) {
          alert("Google didn't return an access token. Check the console for details.");
          return;
        }

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
      error_callback: (error) => {
        console.error("Google sign-in error_callback fired:", error);
        alert("Google sign-in didn't complete: " + (error && error.type ? error.type : "unknown reason") + ". Check the console for details.");
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