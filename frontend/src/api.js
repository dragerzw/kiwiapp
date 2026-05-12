const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
const API_BASE_URL = rawApiBaseUrl.replace(/\/+$/, "");
export const AUTH_INVALID_EVENT = "kiwi:auth-invalid";

const debugEnabled = (() => {
  const envDebug = String(import.meta.env.VITE_ENABLE_DEBUG_TOOLS || "").toLowerCase();
  const envEnabled = ["1", "true", "yes", "on"].includes(envDebug);
  const queryEnabled = new URLSearchParams(globalThis.location.search).has("kiwi_debug");
  return envEnabled || (import.meta.env.DEV && queryEnabled);
})();

const debugLog = (message, details) => {
  if (!debugEnabled) {
    return;
  }
  try {
    console.debug(message, details);
  } catch {
    // Ignore debug logging failures.
  }
};

export class ApiError extends Error {
  constructor(message, status, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

const request = async (endpoint, options = {}, token = null) => {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  debugLog("[kiwi-debug] API request", {
    endpoint,
    method: options.method || "GET",
    tokenPresent: Boolean(token),
  });

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  let data = null;
  const contentType = response.headers.get("content-type");
  if (contentType?.includes("application/json")) {
    data = await response.json();
  }

  if (!response.ok) {
    debugLog("[kiwi-debug] API response error", { endpoint, status: response.status });
    const errorMessage =
      data?.error || data?.message || `Error: ${response.status} ${response.statusText}`;
    if (debugEnabled) {
      try {
        globalThis.__kiwi_last_api_error = {
          endpoint,
          status: response.status,
          message: errorMessage,
          timestamp: new Date().toISOString(),
        };
      } catch {
        // Ignore debug snapshot storage failures.
      }
    }
    if (response.status === 401) {
      globalThis.dispatchEvent(
        new CustomEvent(AUTH_INVALID_EVENT, {
          detail: { message: errorMessage, status: response.status },
        }),
      );
    }
    throw new ApiError(errorMessage, response.status, data);
  }

  return data;
};

export const api = {
  getPortfolios: (token, options = {}) => {
    const searchParams = new URLSearchParams();
    if (options.includeQuotes) {
      searchParams.set("include_quotes", "true");
    }
    const query = searchParams.toString();
    const endpoint = query ? `/portfolios/?${query}` : "/portfolios/";
    return request(endpoint, {}, token);
  },
  createPortfolio: (portfolioData, token) =>
    request("/portfolios/", { method: "POST", body: JSON.stringify(portfolioData) }, token),
  deletePortfolio: (id, token) => request(`/portfolios/${id}`, { method: "DELETE" }, token),
  getTransactions: (id, token) => request(`/portfolios/${id}/transactions`, {}, token),
  getPortfolioDetails: (id, token) => request(`/portfolios/${id}`, {}, token),
  buyTrade: (tradeData, token) =>
    request("/trades/buy", { method: "POST", body: JSON.stringify(tradeData) }, token),
  sellTrade: (tradeData, token) =>
    request("/trades/sell", { method: "POST", body: JSON.stringify(tradeData) }, token),
  getUsers: (token) => request("/user/", {}, token),
};
