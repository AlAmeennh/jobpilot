const API_URL = "http://localhost:8000";

export function getToken() {
  return localStorage.getItem("token");
}

export function clearToken() {
  localStorage.removeItem("token");
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (res.status === 401 && token) {
    // Login expired: go back to the login page
    clearToken();
    window.location.href = "/login";
    throw new Error("Session expired, please log in again");
  }
  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : "Please check your input (password needs at least 8 characters)",
    );
  }
  return data;
}

const jsonHeaders = { "Content-Type": "application/json" };

export function signup(email, password) {
  return request("/auth/signup", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email, password) {
  // The login endpoint expects form data, not JSON
  const body = new URLSearchParams({ username: email, password });
  const data = await request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  localStorage.setItem("token", data.access_token);
  return data;
}

export function listApplications(status) {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return request(`/applications${query}`);
}

export function createApplication(data) {
  return request("/applications", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify(data),
  });
}

export function updateApplication(id, data) {
  return request(`/applications/${id}`, {
    method: "PATCH",
    headers: jsonHeaders,
    body: JSON.stringify(data),
  });
}

export function deleteApplication(id) {
  return request(`/applications/${id}`, { method: "DELETE" });
}
