// ==========================================================
// DevBhumi Horizons — Global JS
// ==========================================================

document.addEventListener("DOMContentLoaded", () => {

  /* 1) Preloader */
  const preloader = document.getElementById("preloader");
  window.addEventListener("load", () => {
    if (preloader) preloader.classList.add("hide");
  });
  setTimeout(() => {
    if (preloader) preloader.classList.add("hide");
  }, 1200);

  /* 2) Sticky / transparent navbar */
  const header = document.getElementById("siteHeader");
  const logo = document.getElementById("siteLogo");
  const isTransparentPage = header && header.classList.contains("is-transparent");

  const handleScroll = () => {
    if (!header)
      return;

    if (isTransparentPage) {

      if (window.scrollY > 60) {
        header.classList.remove("is-transparent");
        header.classList.add("is-solid");

        // Change logo to green
        if (logo) {
          logo.src = "/static/travelingapp/image/DevBhumiLogo_green.png";
        }

      } else {

        header.classList.add("is-transparent");
        header.classList.remove("is-solid");

        // Change logo to white
        if (logo) {
          logo.src = "/static/travelingapp/image/devbhumi-white.png";
        }

      }

    } else {

      header.classList.add("is-solid");

      // Other pages always use green logo
      if (logo) {
        logo.src = "/static/travelingapp/image/DevBhumiLogo_green.png";
      }

    }
  };
  handleScroll();
  window.addEventListener("scroll", handleScroll, { passive: true });

  /* 3) Mobile hamburger menu */
  const navToggle = document.getElementById("navToggle");
  const navMenu = document.getElementById("navMenu");
  const navOverlay = document.getElementById("navOverlay");

  const closeMenu = () => {
    navToggle && navToggle.classList.remove("open");
    navMenu && navMenu.classList.remove("open");
    navOverlay && navOverlay.classList.remove("open");
  };

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", () => {
      navToggle.classList.toggle("open");
      navMenu.classList.toggle("open");
      navOverlay && navOverlay.classList.toggle("open");
    });
    navOverlay && navOverlay.addEventListener("click", closeMenu);
    navMenu.querySelectorAll("a").forEach(link => link.addEventListener("click", closeMenu));
  }

  /* 4) Smooth scroll for in-page anchor links */
  document.querySelectorAll('a[href*="#"]').forEach(link => {
    const href = link.getAttribute("href");
    const hashIndex = href.indexOf("#");
    if (hashIndex === -1) return;
    const hash = href.substring(hashIndex);
    const path = href.substring(0, hashIndex);
    const samePage = path === "" || path === window.location.pathname;
    if (!samePage || hash === "#") return;

    link.addEventListener("click", function (e) {
      const target = document.querySelector(hash);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  /* 5) Back to top button */
  const topButton = document.getElementById("backToTop");
  if (topButton) {
    topButton.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* 6) Reveal-on-scroll (fade up) animation */
  const revealTargets = document.querySelectorAll(
    ".reveal, .package-card, .why-proof-text-box, .transport-box, .hotel-circle, .testimonial-card, .gallery-item, .stat-item, .dest-card"
  );
  revealTargets.forEach(el => el.classList.add("reveal"));

  const appearOnScroll = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        appearOnScroll.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  revealTargets.forEach(el => appearOnScroll.observe(el));

  /* 7) Animated statistic counters */
  const counters = document.querySelectorAll(".stat-number");
  const runCounter = (el) => {
    const target = parseInt(el.dataset.count, 10) || 0;
    const suffix = el.dataset.suffix || "";
    const duration = 1400;
    const start = performance.now();

    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target) + suffix;
      if (progress < 1) requestAnimationFrame(tick);
      else el.textContent = target + suffix;
    };
    requestAnimationFrame(tick);
  };

  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        runCounter(entry.target);
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counters.forEach(el => counterObserver.observe(el));


  /* 8) Testimonial slider (simple auto-rotate for mobile) */
  const track = document.querySelector(".testimonial-track");
  if (track) {
    const cards = track.children.length;
    let index = 0;
    setInterval(() => {
      if (window.innerWidth > 820) return;
      index = (index + 1) % cards;
      track.scrollTo({ left: index * track.clientWidth, behavior: "smooth" });
    }, 4500);
  }

  /* 9) Contact Form → WhatsApp */
  const contactForm = document.getElementById("contactForm");

  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const name = document.getElementById("name").value.trim();
      const email = document.getElementById("email").value.trim();
      const subject = document.getElementById("subject").value.trim();
      const message = document.getElementById("message").value.trim();

      const whatsappMessage =
        `📩 *New Inquiry - DevBhumi Horizons*

        👤 *Name:* ${name}

        📧 *Email:* ${email}

        📌 *Subject:* ${subject}

        💬 *Message:*
        ${message}`;

      const url =
        `https://wa.me/917982479183?text=${encodeURIComponent(whatsappMessage)}`;

      window.open(url, "_blank");

    });

  }



  // const destinations = [
  //   "Kedarnath",
  //   "Badrinath",
  //   "Auli",
  //   "Nainital",
  //   "Mussoorie",
  //   "Rishikesh",
  //   "Haridwar",
  //   "Chopta",
  //   "Valley of Flowers",
  //   "Kedarkantha Trek"
  // ];

  // 10) hero search Destination | Auto search feature
  // const searchInput = document.querySelector("#hs-destination");
  // const searchSuggestion = document.querySelector(".heroSearchSuggestion");
  // let selectedSlug = ""
  // const searchButton = document.querySelector(".hero-search-btn")
  // searchInput.addEventListener("input", function () {

  //   const keyword = searchInput.value.trim();

  //   // Always clear previous suggestions
  //   searchSuggestion.innerHTML = "";

  //   // If input is empty, stop here
  //   if (keyword === "") {
  //     return;
  //   }

  //   // Filter matching destinations
  //   fetch(`/travel/search/?q=${keyword}`).then(
  //     response => response.json()).then(data =>
  //       data.forEach(item => {
  //         const div = document.createElement("div");
  //         div.textContent = item.package_name;
  //         searchSuggestion.appendChild(div);
  //         div.style.color = "white";

  //         div.addEventListener("click", function () {
  //           searchInput.value = item.package_name;
  //           searchSuggestion.innerHTML = ""
  //           selectedSlug = item.slug

  //         })
  //         // div.style.backgroundColor= "black"
  //       }));
  //   // Create suggestions
  // });
  // searchButton.addEventListener("click", function (e) {
  //   e.preventDefault()
  //   if (selectedSlug) {
  //     window.location.href = `/travel/package/${selectedSlug}/`;
  //   }
  // });

   /* 10) Hero destination search — autocomplete dropdown */
  const searchInput = document.querySelector("#hs-destination");
  const searchSuggestion = document.querySelector(".heroSearchSuggestion");
  const searchField = searchInput ? searchInput.closest(".hero-search-field") : null;
  const searchButton = document.querySelector(".hero-search-btn");
  let selectedSlug = "";
  let suggestionTimer = null;
 
  const closeSuggestions = () => {
    if (searchSuggestion) searchSuggestion.innerHTML = "";
  };
  
  const renderSuggestions = (items, keyword) => {
    if (!searchSuggestion) return;
    searchSuggestion.innerHTML = "";
 
    items.forEach(item => {
      const row = document.createElement("div");
      row.className = "suggestion-item";
      row.innerHTML = `<i class="fa-solid fa-location-dot"></i><span>${item.package_name}</span>`;
 
      row.addEventListener("click", function () {
        searchInput.value = item.package_name;
        selectedSlug = item.slug;
        closeSuggestions();
      });
 
      searchSuggestion.appendChild(row);
    });
 
    // "View all results" row — always shown under whatever matches came back
    const viewAllRow = document.createElement("div");
    viewAllRow.className = "suggestion-viewall";
    viewAllRow.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i><span>View all results for "${keyword}"</span>`;
    viewAllRow.addEventListener("click", function () {
      window.location.href = `/travel/explore/?destination=${encodeURIComponent(keyword)}`;
    });
    searchSuggestion.appendChild(viewAllRow);
  };
 
  if (searchInput && searchSuggestion) {
    searchInput.addEventListener("input", function () {
      const keyword = searchInput.value.trim();
 
      // any manual edit invalidates a previously picked suggestion
      selectedSlug = "";
      clearTimeout(suggestionTimer);
      closeSuggestions();
 
      if (keyword === "") return;
 
      suggestionTimer = setTimeout(() => {
        fetch(`/travel/search/?q=${encodeURIComponent(keyword)}`)
          .then(response => response.json())
          .then(data => renderSuggestions(data, keyword))
          .catch(() => closeSuggestions());
      }, 200);
    });
 
    searchInput.addEventListener("focus", function () {
      if (searchInput.value.trim() !== "" && searchSuggestion.innerHTML === "") {
        searchInput.dispatchEvent(new Event("input"));
      }
    });
    
    // this is for close the searchSuggestion if use click outside the search box
    document.addEventListener("click", function (e) {
      if (searchField && !searchField.contains(e.target)) closeSuggestions();
    });
 
    searchInput.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeSuggestions();
    });
  }
 
  if (searchButton) {
    searchButton.addEventListener("click", function (e) {
      e.preventDefault();
      if (selectedSlug) {
        window.location.href = `/travel/package/${selectedSlug}/`;
      } else if (searchInput && searchInput.value.trim()) {
        window.location.href = `/travel/explore/?destination=${encodeURIComponent(searchInput.value.trim())}`;
      }
    });
  }

  // 11 for login/SignUp
  // const overlay = document.getElementById("authModalOverlay");
  // if (!overlay) return; // partial not included on this page
 
  // const modal = document.getElementById("authModal");
  // const closeBtn = document.getElementById("authModalClose");
  // const bodyLogin = document.getElementById("authBodyLogin");
  // const bodySignup = document.getElementById("authBodySignup");
  // const showSignupBtn = document.getElementById("showSignupBtn");
  // const showLoginBtn = document.getElementById("showLoginBtn");
  // const loginForm = document.getElementById("loginForm");
  // const signupForm = document.getElementById("signupForm");
 
  // const openModal = (mode = "login") => {
  //   mode === "signup" ? switchTo("signup") : switchTo("login");
  //   overlay.classList.add("open");
  //   document.body.classList.add("auth-modal-open");
  // };
 
  // const closeModal = () => {
  //   overlay.classList.remove("open");
  //   document.body.classList.remove("auth-modal-open");
  // };
 
  // const switchTo = (mode) => {
  //   const showSignup = mode === "signup";
  //   bodyLogin.hidden = showSignup;
  //   bodySignup.hidden = !showSignup;
  // };
 
  // // Open triggers — any element with data-auth-trigger="login" / "signup"
  // document.querySelectorAll("[data-auth-trigger]").forEach(trigger => {
  //   trigger.addEventListener("click", (e) => {
  //     e.preventDefault();
  //     openModal(trigger.dataset.authTrigger || "login");
  //   });
  // });
 
  // // Close interactions
  // closeBtn.addEventListener("click", closeModal);
  // overlay.addEventListener("click", (e) => {
  //   if (e.target === overlay) closeModal();
  // });
  // document.addEventListener("keydown", (e) => {
  //   if (e.key === "Escape" && overlay.classList.contains("open")) closeModal();
  // });
 
  // // Switch between login / signup panes
  // showSignupBtn && showSignupBtn.addEventListener("click", () => switchTo("signup"));
  // showLoginBtn && showLoginBtn.addEventListener("click", () => switchTo("login"));
 
  // // Show/hide password
  // document.querySelectorAll(".auth-toggle-pass").forEach(btn => {
  //   btn.addEventListener("click", () => {
  //     const input = document.getElementById(btn.dataset.target);
  //     if (!input) return;
  //     const icon = btn.querySelector("i");
  //     const isHidden = input.type === "password";
  //     input.type = isHidden ? "text" : "password";
  //     icon.classList.toggle("fa-eye-slash", !isHidden);
  //     icon.classList.toggle("fa-eye", isHidden);
  //   });
  // });
 
  // // ---- Form submits ----
  // // TODO: point these at your real Django auth endpoints
  // // (e.g. {% url 'login' %} / {% url 'signup' %}) once they exist —
  // // for now they're intercepted so the modal doesn't just hard-navigate.
  // if (loginForm) {
  //   loginForm.addEventListener("submit", (e) => {
  //     e.preventDefault();
  //     console.log("Login submitted:", {
  //       email: loginForm.email.value,
  //       password: loginForm.password.value,
  //     });
  //     // fetch('/accounts/login/', { method: 'POST', body: new FormData(loginForm) })
  //   });
  // }
 
  // if (signupForm) {
  //   signupForm.addEventListener("submit", (e) => {
  //     e.preventDefault();
  //     console.log("Signup submitted:", {
  //       name: signupForm.name.value,
  //       email: signupForm.email.value,
  //       password: signupForm.password.value,
  //       confirmPassword: signupForm.confirmPassword.value
  //     });
  //     // fetch('/accounts/signup/', { method: 'POST', body: new FormData(signupForm) })
  //   });
  // }

  // ==========================================================
  // 11) User Profile Dropdown
  // ==========================================================

  // const userBtn = document.getElementById("userBtn");
  // const userDropdown = document.getElementById("userDropdown");

  // if (userBtn && userDropdown) {

  //   userBtn.addEventListener("click", (e) => {
  //     e.stopPropagation();

  //     userDropdown.classList.toggle("show");
  //   });

  //   // Click outside → dropdown close
  //   document.addEventListener("click", (e) => {
  //     if (!userBtn.contains(e.target) && !userDropdown.contains(e.target)) {
  //       userDropdown.classList.remove("show");
  //     }
  //   });

  // }

  
  // function getCookie(name) {
  //   const match = document.cookie.match(
  //     new RegExp("(^| )" + name + "=([^;]+)")
  //   );

  //   return match ? match[2] : null;
  // }
  // const logoutBtn = document.getElementById("logoutBtn");

  // if (logoutBtn) {
  //   logoutBtn.addEventListener("click", () => {

  //     fetch("/travel/auth/logout/", {
  //       method: "POST",

  //       headers: {
  //         "X-CSRFToken": getCookie("csrftoken"),
  //       },

  //     })
  //       .then(res => res.json())
  //       .then(data => {

  //         if (data.success) {
  //           window.location.reload();
  //         }

  //       })
  //       .catch(() => {
  //         alert("Logout failed. Please try again.");
  //       });

  //   });

  // }
  console.log("DevBhumi Horizons — Explore Uttarakhand with heart!");

});


