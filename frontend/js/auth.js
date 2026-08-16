// Auth Functions - COMPLETE FIXED VERSION

async function register(userData) {
  console.log("Registering with data:", { ...userData, password: "***" });

  try {
    const response = await api.post("/auth/register", userData);
    console.log("Registration response:", response);

    if (response.access_token) {
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("refresh_token", response.refresh_token);
      await loadUserProfile();
      navigateTo("home");
      showToast("Registration successful! Welcome to NepaliFashion", "success");
    }
    return response;
  } catch (error) {
    console.error("Registration error:", error);
    showToast(error.message || "Registration failed", "error");
    throw error;
  }
}

async function login(username, password) {
  console.log("Logging in with username:", username);

  try {
    const response = await api.post("/auth/login", {
      username: username.trim(),
      password: password,
    });
    console.log("Login response received");

    if (response.access_token) {
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("refresh_token", response.refresh_token);
      await loadUserProfile();
      navigateTo("home");
      showToast("Welcome back, " + username + "!", "success");
    }
    return response;
  } catch (error) {
    console.error("Login error:", error);
    showToast(error.message || "Login failed", "error");
    throw error;
  }
}

async function logout() {
  try {
    await api.post("/auth/logout");
  } catch (error) {
    console.error("Logout error:", error);
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");

    // Update UI
    const authSection = document.getElementById("auth-section");
    const userSection = document.getElementById("user-section");
    if (authSection) authSection.style.display = "flex";
    if (userSection) userSection.style.display = "none";

    navigateTo("home");
    showToast("Logged out successfully", "success");
  }
}

async function loadUserProfile() {
  try {
    const user = await api.get("/users/me");
    localStorage.setItem("user", JSON.stringify(user));

    const authSection = document.getElementById("auth-section");
    const userSection = document.getElementById("user-section");
    const usernameDisplay = document.getElementById("username-display");

    if (authSection) authSection.style.display = "none";
    if (userSection) userSection.style.display = "flex";
    if (usernameDisplay) usernameDisplay.textContent = `👋 ${user.username}`;

    return user;
  } catch (error) {
    console.error("Failed to load profile:", error);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    throw error;
  }
}

function getCurrentUser() {
  const userData = localStorage.getItem("user");
  return userData ? JSON.parse(userData) : null;
}

function isAuthenticated() {
  return !!localStorage.getItem("access_token");
}

// Check auth status on page load
document.addEventListener("DOMContentLoaded", async () => {
  if (isAuthenticated()) {
    try {
      await loadUserProfile();
    } catch (error) {
      console.error("Auth check failed:", error);
    }
  }
});
