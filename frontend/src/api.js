const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
const API_BASE_URL = rawApiBaseUrl.replace(/\/+$/, "");
export const AUTH_INVALID_EVENT = "kiwi:auth-invalid";

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

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  let data = null;
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    data = await response.json();
  }

  if (!response.ok) {
    const errorMessage =
      data?.error || data?.message || `Error: ${response.status} ${response.statusText}`;
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
};
