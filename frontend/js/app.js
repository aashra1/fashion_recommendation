// Main Application Logic

const DEFAULT_PAGE = "home";

function buildHashRoute(page = DEFAULT_PAGE, params = {}) {
  const route = page === DEFAULT_PAGE ? "" : page;
  const query = new URLSearchParams(params).toString();
  return `#/${route}${query ? `?${query}` : ""}`;
}

function parseHashRoute() {
  const rawHash = window.location.hash.replace(/^#\/?/, "");
  const [pagePart, queryPart] = rawHash.split("?");
  const page = pagePart || DEFAULT_PAGE;
  const params = Object.fromEntries(new URLSearchParams(queryPart || ""));
  return { page, params };
}

// Navigation
function navigateTo(page, params = {}, replace = false) {
  const hash = buildHashRoute(page, params);
  if (replace) {
    window.history.replaceState({ page, params }, "", hash);
  } else {
    window.history.pushState({ page, params }, "", hash);
  }
  renderPage(page, params);
}

// Page Renderer
async function renderPage(page, params = {}) {
  switch (page) {
    case "home":
      await renderHomePage();
      break;
    case "products":
      await loadProducts(Number(params.page || 1), params);
      break;
    case "product":
      if (params.id) {
        await loadProductDetail(params.id);
      } else {
        navigateTo("products");
      }
      break;
    case "login":
      renderLoginPage();
      break;
    case "register":
      renderRegisterPage();
      break;
    case "profile":
      await renderProfilePage();
      break;
    default:
      await renderHomePage();
  }
}

// Login Page
function renderLoginPage() {
  if (isAuthenticated()) {
    navigateTo("home");
    return;
  }

  const content = document.getElementById("content");
  if (!content) return;

  content.innerHTML = `
        <div class="container mx-auto px-4 py-8">
            <div class="auth-container">
                <h2>Welcome Back</h2>
                <p class="subtitle">Login to your NepaliFashion account</p>
                
                <form onsubmit="handleLogin(event)" id="login-form">
                    <div class="form-group">
                        <label for="login-username">Username</label>
                        <input type="text" id="login-username" required placeholder="Enter your username">
                    </div>
                    
                    <div class="form-group">
                        <label for="login-password">Password</label>
                        <input type="password" id="login-password" required placeholder="Enter your password">
                    </div>
                    
                    <div id="login-error" class="error-message" style="display:none;"></div>
                    
                    <button type="submit" class="btn-primary">Login</button>
                </form>
                
                <div class="link">
                    Don't have an account? <a href="#" onclick="navigateTo('register')">Register</a>
                </div>
            </div>
        </div>
    `;
}

// Register Page - With First Name and Last Name
function renderRegisterPage() {
  if (isAuthenticated()) {
    navigateTo("home");
    return;
  }

  const content = document.getElementById("content");
  if (!content) return;

  content.innerHTML = `
        <div class="container mx-auto px-4 py-8">
            <div class="auth-container">
                <h2>Create Account</h2>
                <p class="subtitle">Join NepaliFashion for personalized recommendations</p>
                
                <form onsubmit="handleRegister(event)" id="register-form">
                    <!-- First Name & Last Name Row -->
                    <div class="name-grid">
                        <div class="form-group">
                            <label for="reg-firstname">First Name</label>
                            <input type="text" id="reg-firstname" placeholder="Enter your first name">
                        </div>
                        <div class="form-group">
                            <label for="reg-lastname">Last Name</label>
                            <input type="text" id="reg-lastname" placeholder="Enter your last name">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="reg-username">Username</label>
                        <input type="text" id="reg-username" required placeholder="Choose a username">
                    </div>
                    
                    <div class="form-group">
                        <label for="reg-email">Email</label>
                        <input type="email" id="reg-email" required placeholder="Enter your email">
                    </div>
                    
                    <div class="form-group">
                        <label for="reg-password">Password</label>
                        <input type="password" id="reg-password" required placeholder="Create a password (min 6 chars)">
                    </div>
                    
                    <div class="form-group">
                        <label>Preferred Categories</label>
                        <div class="checkbox-grid">
                            ${[
                              "Men",
                              "Women",
                              "Kids",
                              "Traditional",
                              "Accessories",
                            ]
                              .map(
                                (cat) => `
                                <label class="checkbox-option">
                                    <input type="checkbox" value="${cat}" class="reg-category"> ${cat}
                                </label>
                            `,
                              )
                              .join("")}
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>Preferred Styles</label>
                        <div class="checkbox-grid">
                            ${[
                              "Casual",
                              "Formal",
                              "Sport",
                              "Traditional",
                              "Winter",
                            ]
                              .map(
                                (style) => `
                                <label class="checkbox-option">
                                    <input type="checkbox" value="${style}" class="reg-style"> ${style}
                                </label>
                            `,
                              )
                              .join("")}
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="reg-location">Location</label>
                        <select id="reg-location">
                            <option value="">Select your city</option>
                            ${[
                              "Kathmandu",
                              "Pokhara",
                              "Biratnagar",
                              "Lalitpur",
                              "Bhaktapur",
                              "Other",
                            ]
                              .map(
                                (loc) => `
                                <option value="${loc}">${loc}</option>
                            `,
                              )
                              .join("")}
                        </select>
                    </div>
                    
                    <div id="register-error" class="error-message" style="display:none;"></div>
                    
                    <button type="submit" class="btn-primary">Create Account</button>
                </form>
                
                <div class="link">
                    Already have an account? <a href="#" onclick="navigateTo('login')">Login</a>
                </div>
            </div>
        </div>
    `;
}

// Profile Page
async function renderProfilePage() {
  if (!isAuthenticated()) {
    navigateTo("login");
    return;
  }

  let user = getCurrentUser();
  if (!user) {
    try {
      user = await loadUserProfile();
    } catch (error) {
      navigateTo("login");
      return;
    }
  }

  const content = document.getElementById("content");
  if (!content) return;

  const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");
  const displayName = fullName || user.username;
  const initials = displayName
    .split(" ")
    .map((part) => part.charAt(0))
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const preferredCategories = user.preferred_categories || [];
  const preferredStyles = user.preferred_styles || [];

  content.innerHTML = `
        <div class="profile-page">
            <section class="profile-header">
                <div class="profile-avatar">${initials}</div>
                <div class="profile-heading">
                    <p class="profile-kicker">Recommendation Profile</p>
                    <h1>${displayName}</h1>
                    <p>${user.email}</p>
                </div>
                <div class="profile-actions">
                    <button type="button" onclick="navigateTo('products')" class="profile-secondary-btn">Browse Products</button>
                    <button type="button" onclick="logout()" class="profile-danger-btn">Logout</button>
                </div>
            </section>

            <div class="profile-grid">
                <aside class="profile-summary">
                    <div class="summary-card">
                        <span class="summary-label">Username</span>
                        <strong>${user.username}</strong>
                    </div>
                    <div class="summary-card">
                        <span class="summary-label">Location</span>
                        <strong>${user.location || "Not set"}</strong>
                    </div>
                    <div class="summary-card">
                        <span class="summary-label">Budget</span>
                        <strong>Rs. ${user.preferred_price_min || 0} - Rs. ${user.preferred_price_max || 100000}</strong>
                    </div>
                    <div class="profile-chip-panel">
                        <span class="summary-label">Category Signals</span>
                        <div class="profile-chip-list">
                            ${
                              preferredCategories.length
                                ? preferredCategories.map((cat) => `<span>${cat}</span>`).join("")
                                : "<span>Traditional</span>"
                            }
                        </div>
                    </div>
                    <div class="profile-chip-panel">
                        <span class="summary-label">Style Signals</span>
                        <div class="profile-chip-list">
                            ${
                              preferredStyles.length
                                ? preferredStyles.map((style) => `<span>${style}</span>`).join("")
                                : "<span>Casual</span>"
                            }
                        </div>
                    </div>
                </aside>

                <section class="profile-editor">
                    <div class="profile-section-title">
                        <h2>Personal Details</h2>
                        <p>These details help tune Nepali fashion recommendations around your context.</p>
                    </div>

                    <form onsubmit="handleProfileUpdate(event)" id="profile-form">
                        <div class="profile-form-grid">
                            <div class="profile-field">
                                <label for="profile-first-name">First Name</label>
                                <input type="text" id="profile-first-name" value="${user.first_name || ""}" placeholder="First name">
                            </div>
                            <div class="profile-field">
                                <label for="profile-last-name">Last Name</label>
                                <input type="text" id="profile-last-name" value="${user.last_name || ""}" placeholder="Last name">
                            </div>
                            <div class="profile-field">
                                <label for="profile-location">Location</label>
                                <select id="profile-location">
                                    ${[
                                      "Kathmandu",
                                      "Pokhara",
                                      "Biratnagar",
                                      "Lalitpur",
                                      "Bhaktapur",
                                      "Other",
                                    ]
                                      .map(
                                        (loc) => `
                                        <option value="${loc}" ${user.location === loc ? "selected" : ""}>${loc}</option>
                                    `,
                                      )
                                      .join("")}
                                </select>
                            </div>
                        </div>

                        <div class="profile-divider"></div>

                        <div class="profile-section-title">
                            <h2>Recommendation Preferences</h2>
                            <p>Select the fashion signals the AI should prioritize.</p>
                        </div>

                        <div class="profile-preference-block">
                            <label class="profile-group-label">Preferred Categories</label>
                            <div class="profile-option-grid">
                                ${[
                                  "Men",
                                  "Women",
                                  "Kids",
                                  "Traditional",
                                  "Accessories",
                                ]
                                  .map(
                                    (cat) => `
                                    <label class="profile-option-card">
                                        <input type="checkbox" value="${cat}" class="profile-category"
                                               ${preferredCategories.includes(cat) ? "checked" : ""}>
                                        <span>${cat}</span>
                                    </label>
                                `,
                                  )
                                  .join("")}
                            </div>
                        </div>

                        <div class="profile-preference-block">
                            <label class="profile-group-label">Preferred Styles</label>
                            <div class="profile-option-grid">
                                ${[
                                  "Casual",
                                  "Formal",
                                  "Sport",
                                  "Traditional",
                                  "Winter",
                                ]
                                  .map(
                                    (style) => `
                                    <label class="profile-option-card">
                                        <input type="checkbox" value="${style}" class="profile-style"
                                               ${preferredStyles.includes(style) ? "checked" : ""}>
                                        <span>${style}</span>
                                    </label>
                                `,
                                  )
                                  .join("")}
                            </div>
                        </div>

                        <div class="profile-price-row">
                            <div class="profile-field">
                                <label for="profile-price-min">Minimum Price (NPR)</label>
                                <input type="number" id="profile-price-min" min="0" value="${user.preferred_price_min || 0}">
                            </div>
                            <div class="profile-field">
                                <label for="profile-price-max">Maximum Price (NPR)</label>
                                <input type="number" id="profile-price-max" min="0" value="${user.preferred_price_max || 100000}">
                            </div>
                        </div>

                        <div id="profile-error" class="profile-error" style="display:none;"></div>

                        <div class="profile-submit-row">
                            <button type="button" onclick="navigateTo('home')" class="profile-secondary-btn">Cancel</button>
                            <button type="submit" class="profile-primary-btn">Save Profile</button>
                        </div>
                    </form>
                </section>
            </div>
        </div>
    `;
}

// Form Handlers - FIXED VERSION

async function handleLogin(event) {
  event.preventDefault();

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;
  const errorEl = document.getElementById("login-error");

  // Clear previous error
  errorEl.style.display = "none";
  errorEl.textContent = "";

  // Validate
  if (!username || !password) {
    errorEl.textContent = "Please enter both username and password";
    errorEl.style.display = "block";
    return;
  }

  console.log("🔐 Attempting login with username:", username);

  try {
    await login(username, password);
  } catch (error) {
    console.error("❌ Login error:", error);
    errorEl.textContent = error.message || "Login failed. Please try again.";
    errorEl.style.display = "block";
  }
}

async function handleRegister(event) {
  event.preventDefault();

  const errorEl = document.getElementById("register-error");
  errorEl.style.display = "none";
  errorEl.textContent = "";

  // Get form values
  const firstName =
    document.getElementById("reg-firstname")?.value.trim() || "";
  const lastName = document.getElementById("reg-lastname")?.value.trim() || "";
  const username = document.getElementById("reg-username").value.trim();
  const email = document.getElementById("reg-email").value.trim();
  const password = document.getElementById("reg-password").value;

  // Validate
  if (!username || username.length < 3) {
    errorEl.textContent = "Username must be at least 3 characters";
    errorEl.style.display = "block";
    return;
  }

  if (!email || !email.includes("@")) {
    errorEl.textContent = "Please enter a valid email address";
    errorEl.style.display = "block";
    return;
  }

  if (!password || password.length < 6) {
    errorEl.textContent = "Password must be at least 6 characters";
    errorEl.style.display = "block";
    return;
  }

  // Get selected categories and styles
  const categories = Array.from(
    document.querySelectorAll(".reg-category:checked"),
  ).map((cb) => cb.value);

  const styles = Array.from(
    document.querySelectorAll(".reg-style:checked"),
  ).map((cb) => cb.value);

  // Build user data object - MATCHES BACKEND SCHEMA
  const userData = {
    username: username,
    email: email,
    password: password,
    first_name: firstName,
    last_name: lastName,
    preferred_categories: categories.length > 0 ? categories : ["Traditional"],
    preferred_styles: styles.length > 0 ? styles : ["Casual"],
    preferred_price_min: 0,
    preferred_price_max: 100000,
    location: document.getElementById("reg-location").value || "Kathmandu",
  };

  console.log("📝 Registering with:", {
    ...userData,
    password: "***",
  });

  try {
    await register(userData);
  } catch (error) {
    console.error("❌ Registration error:", error);
    errorEl.textContent =
      error.message || "Registration failed. Please try again.";
    errorEl.style.display = "block";
  }
}

async function handleProfileUpdate(event) {
  event.preventDefault();

  const errorEl = document.getElementById("profile-error");
  errorEl.style.display = "none";
  errorEl.textContent = "";

  const categories = Array.from(
    document.querySelectorAll(".profile-category:checked"),
  ).map((cb) => cb.value);

  const styles = Array.from(
    document.querySelectorAll(".profile-style:checked"),
  ).map((cb) => cb.value);

  const minPrice =
    parseFloat(document.getElementById("profile-price-min").value) || 0;
  const maxPrice =
    parseFloat(document.getElementById("profile-price-max").value) || 100000;

  if (maxPrice < minPrice) {
    errorEl.textContent = "Maximum price must be greater than minimum price";
    errorEl.style.display = "block";
    return;
  }

  const userData = {
    first_name: document.getElementById("profile-first-name").value.trim(),
    last_name: document.getElementById("profile-last-name").value.trim(),
    location: document.getElementById("profile-location").value,
    preferred_categories: categories,
    preferred_styles: styles,
    preferred_price_min: minPrice,
    preferred_price_max: maxPrice,
  };

  try {
    const updated = await api.put("/users/me", userData);
    localStorage.setItem("user", JSON.stringify(updated));
    showToast("Preferences updated successfully!", "success");
    navigateTo("home");
  } catch (error) {
    console.error("❌ Profile update error:", error);
    errorEl.textContent = error.message || "Update failed. Please try again.";
    errorEl.style.display = "block";
  }
}

window.addEventListener("hashchange", () => {
  const { page, params } = parseHashRoute();
  renderPage(page, params);
});

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  const { page, params } = parseHashRoute();
  if (!window.location.hash) {
    navigateTo(DEFAULT_PAGE, {}, true);
  } else {
    renderPage(page, params);
  }
});

// Make functions globally available
window.navigateTo = navigateTo;
window.logout = logout;
window.showToast = showToast;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.handleProfileUpdate = handleProfileUpdate;
