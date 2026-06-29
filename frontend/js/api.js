/**
 * Monika G Cafe — API client
 * ---------------------------------------------------------------
 * Every fetch call to the backend goes through here. Centralizing
 * this means:
 *   1. The JSON field names sent/received always match the FastAPI
 *      Pydantic schemas exactly (see backend/app/schemas/*.py).
 *   2. The JWT access token is attached automatically.
 *   3. A 401 (expired token) triggers one silent refresh attempt
 *      before giving up and sending the user back to login.
 *
 * Change BASE_URL if your backend runs somewhere other than
 * http://localhost:8000.
 */
const API = (() => {
  const BASE_URL = window.MONIKA_API_BASE_URL || "http://localhost:8000";

  function getAccessToken() {
    return localStorage.getItem("mg_access_token");
  }
  function getRefreshToken() {
    return localStorage.getItem("mg_refresh_token");
  }
  function setTokens(access, refresh) {
    localStorage.setItem("mg_access_token", access);
    localStorage.setItem("mg_refresh_token", refresh);
  }
  function setUser(user) {
    localStorage.setItem("mg_user", JSON.stringify(user));
  }
  function getUser() {
    const raw = localStorage.getItem("mg_user");
    return raw ? JSON.parse(raw) : null;
  }
  function clearSession() {
    localStorage.removeItem("mg_access_token");
    localStorage.removeItem("mg_refresh_token");
    localStorage.removeItem("mg_user");
  }

  async function refreshAccessToken() {
    const refresh_token = getRefreshToken();
    if (!refresh_token) return false;
    try {
      const res = await fetch(`${BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      setTokens(data.access_token, data.refresh_token);
      setUser(data.user);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Core request function.
   * @param {string} path - e.g. "/orders"
   * @param {object} options - { method, body, auth }
   */
  async function request(path, { method = "GET", body, auth = true, retry = true } = {}) {
    const headers = { "Content-Type": "application/json" };
    if (auth) {
      const token = getAccessToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (res.status === 401 && auth && retry) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return request(path, { method, body, auth, retry: false });
      }
      clearSession();
      window.location.href = "login.html";
      throw new Error("Session expired. Please log in again.");
    }

    let data = null;
    try {
      data = await res.json();
    } catch {
      /* no JSON body, e.g. some 204 responses */
    }

    if (!res.ok) {
      const message = (data && (data.detail || data.message)) || `Request failed (${res.status})`;
      throw new Error(typeof message === "string" ? message : JSON.stringify(message));
    }
    return data;
  }

  return {
    BASE_URL,
    getAccessToken,
    getRefreshToken,
    setTokens,
    getUser,
    setUser,
    clearSession,

    // ---------- Auth ----------
    auth: {
      requestEmailOtp: (email) =>
        request("/auth/email/request-otp", { method: "POST", body: { email }, auth: false }),
      verifyEmailOtp: (email, otp_code) =>
        request("/auth/email/verify-otp", { method: "POST", body: { email, otp_code }, auth: false }),
      requestMobileOtp: (phone) =>
        request("/auth/mobile/request-otp", { method: "POST", body: { phone }, auth: false }),
      verifyMobileOtp: (phone, otp_code) =>
        request("/auth/mobile/verify-otp", { method: "POST", body: { phone, otp_code }, auth: false }),
      googleLogin: (id_token) =>
        request("/auth/google", { method: "POST", body: { id_token }, auth: false }),
      me: () => request("/auth/me"),
    },

    // ---------- Menu ----------
    menu: {
      listCategories: () => request("/menu/categories", { auth: false }),
      createCategory: (name) => request("/menu/categories", { method: "POST", body: { name } }),
      list: (params = {}) => {
        const qs = new URLSearchParams(params).toString();
        return request(`/menu${qs ? "?" + qs : ""}`, { auth: false });
      },
      get: (id) => request(`/menu/${id}`, { auth: false }),
      create: (payload) => request("/menu", { method: "POST", body: payload }),
      update: (id, payload) => request(`/menu/${id}`, { method: "PUT", body: payload }),
      remove: (id) => request(`/menu/${id}`, { method: "DELETE" }),
    },

    // ---------- Inventory ----------
    inventory: {
      list: (lowStockOnly = false) =>
        request(`/inventory${lowStockOnly ? "?low_stock_only=true" : ""}`),
      create: (payload) => request("/inventory", { method: "POST", body: payload }),
      update: (id, payload) => request(`/inventory/${id}`, { method: "PUT", body: payload }),
      adjust: (id, change_amount, reason) =>
        request(`/inventory/${id}/adjust`, { method: "POST", body: { change_amount, reason } }),
      remove: (id) => request(`/inventory/${id}`, { method: "DELETE" }),
    },

    // ---------- Orders ----------
    orders: {
      create: (payload) => request("/orders", { method: "POST", body: payload }),
      list: (statusFilter) =>
        request(`/orders${statusFilter ? "?status_filter=" + statusFilter : ""}`),
      get: (id) => request(`/orders/${id}`),
      updateStatus: (id, statusValue) =>
        request(`/orders/${id}/status`, { method: "PATCH", body: { status: statusValue } }),
      kitchenQueue: () => request("/orders/kitchen/queue"),
    },

    // ---------- Bills ----------
    bills: {
      create: (payload) => request("/bills", { method: "POST", body: payload }),
      list: (unpaidOnly = false) => request(`/bills${unpaidOnly ? "?unpaid_only=true" : ""}`),
      get: (id) => request(`/bills/${id}`),
      updatePayment: (id, is_paid, payment_method) =>
        request(`/bills/${id}/payment`, { method: "PATCH", body: { is_paid, payment_method } }),
    },

    // ---------- Employees ----------
    employees: {
      list: () => request("/employees"),
      create: (payload) => request("/employees", { method: "POST", body: payload }),
      update: (id, payload) => request(`/employees/${id}`, { method: "PUT", body: payload }),
      remove: (id) => request(`/employees/${id}`, { method: "DELETE" }),
      markAttendance: (employee_id, status) =>
        request("/employees/attendance", { method: "POST", body: { employee_id, status } }),
    },

    // ---------- Reports ----------
    reports: {
      dashboard: () => request("/reports/dashboard"),
      sales: (start_date, end_date) => {
        const params = {};
        if (start_date) params.start_date = start_date;
        if (end_date) params.end_date = end_date;
        const qs = new URLSearchParams(params).toString();
        return request(`/reports/sales${qs ? "?" + qs : ""}`);
      },
      topItems: (limit = 5) => request(`/reports/top-items?limit=${limit}`),
    },
  };
})();
