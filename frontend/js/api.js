const API_BASE_URL = (() => {
    const origin = window.location.origin;
    if (origin && origin !== "null" && /:8000$/.test(origin)) {
        return origin;
    }
    return "http://127.0.0.1:8000";
})();

const AUTH_TOKEN_KEY = "academic_portal_token";
const AUTH_USER_KEY = "academic_portal_user";

function getAuthToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
}

function setAuthSession(token, user) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

function clearAuthSession() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
}

function redirectToLogin() {
    clearAuthSession();
    window.location.href = "login.html";
}

async function apiRequest(path, options = {}) {
    const headers = new Headers(options.headers || {});
    if (!headers.has("Content-Type") && options.body) {
        headers.set("Content-Type", "application/json");
    }

    const token = getAuthToken();
    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers,
    });
    const data = await response.json().catch(() => ({}));

    if (response.status === 401) {
        redirectToLogin();
        throw new Error("Please sign in again.");
    }

    if (!response.ok) {
        throw new Error(data.detail || "Request failed.");
    }

    return data;
}

async function loginWithDatabase(email, password) {
    const data = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
    });
    setAuthSession(data.access_token, data.user);
    return data.user;
}

async function requireStudentSession() {
    const token = getAuthToken();
    if (!token) {
        redirectToLogin();
        throw new Error("Please sign in first.");
    }
    const student = await apiRequest("/students/me");
    if (student.role !== "student") {
        redirectToLogin();
        throw new Error("A student account is required.");
    }
    return student;
}

async function requireAdminSession() {
    const token = getAuthToken();
    if (!token) {
        redirectToLogin();
        throw new Error("Please sign in first.");
    }
    const admin = await apiRequest("/admin/me");
    if (admin.role !== "admin") {
        redirectToLogin();
        throw new Error("An admin account is required.");
    }
    return admin;
}

function setText(selector, value) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = value ?? "Not provided";
    }
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function ordinal(value) {
    const number = Number(value);
    if (!number) {
        return "Not provided";
    }
    const suffix = number === 1 ? "st" : number === 2 ? "nd" : number === 3 ? "rd" : "th";
    return `${number}${suffix}`;
}

function formatDate(value) {
    if (!value) {
        return "Not provided";
    }
    return new Intl.DateTimeFormat("en", {
        year: "numeric",
        month: "short",
        day: "numeric",
    }).format(new Date(value));
}
