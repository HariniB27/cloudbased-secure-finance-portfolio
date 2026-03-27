import axios from "axios";

const API_BASE = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth
export const login = (username: string, password: string, recaptchaToken: string) =>
  api.post("/auth/login", { username, password, recaptcha_token: recaptchaToken });

export const register = (email: string, username: string, password: string, recaptchaToken: string) =>
  api.post("/auth/register", { email, username, password, recaptcha_token: recaptchaToken });

export const forgotPassword = (email: string, recaptchaToken: string) =>
  api.post("/auth/forgot-password", { email, recaptcha_token: recaptchaToken });

export const resetPassword = (token: string, newPassword: string, recaptchaToken: string) =>
  api.post("/auth/reset-password", { token, new_password: newPassword, recaptcha_token: recaptchaToken });

// Portfolio
export const getPortfolioSummary = () => api.get("/portfolio/summary");
export const refreshPortfolio = () => api.post("/portfolio/refresh");
export const getPerformanceMetrics = () => api.get("/portfolio/performance");

// Assets
export const getAssets = () => api.get("/assets");
export const addAsset = (data: Record<string, unknown>) => api.post("/assets", data);
export const updateAsset = (id: string | number, data: Record<string, unknown>) =>
  api.put(`/assets/${id}`, data);
export const deleteAsset = (id: string | number) => api.delete(`/assets/${id}`);

// Risk
export const predictRisk = () => api.post("/risk/predict");

// Advisor
export const getAdvice = () => api.post("/advisor");

// Export
export const downloadPortfolioReport = () =>
  api.get("/export/pdf", {
    responseType: "blob",
  });

export default api;
