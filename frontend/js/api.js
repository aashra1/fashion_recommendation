// API Configuration
const API_BASE_URL = "http://localhost:8000/api";

// API Client with better error handling
const api = {
  async request(endpoint, method = "GET", data = null, headers = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    // Add auth token if available
    const token = localStorage.getItem("access_token");
    if (token) {
      options.headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, options);
      const contentType = response.headers.get("content-type") || "";
      const responseData = contentType.includes("application/json")
        ? await response.json()
        : null;

      if (!response.ok) {
        // Extract error message
        const errorMsg =
          responseData?.detail ||
          responseData?.message ||
          response.statusText ||
          "Request failed";
        const error = new Error(errorMsg);
        error.status = response.status;
        error.response = responseData;
        throw error;
      }

      return responseData;
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  },

  get(endpoint, headers = {}) {
    return this.request(endpoint, "GET", null, headers);
  },

  post(endpoint, data, headers = {}) {
    return this.request(endpoint, "POST", data, headers);
  },

  put(endpoint, data, headers = {}) {
    return this.request(endpoint, "PUT", data, headers);
  },

  delete(endpoint, headers = {}) {
    return this.request(endpoint, "DELETE", null, headers);
  },
};

// Toast notifications
function showToast(message, type = "success") {
  const toast = document.getElementById("toast") || createToast();
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function createToast() {
  const toast = document.createElement("div");
  toast.id = "toast";
  toast.className = "toast";
  document.body.appendChild(toast);
  return toast;
}

// Make showToast globally available
window.showToast = showToast;
