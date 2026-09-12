import axios from "axios"; // Axios is a JavaScript library that lets frontend make HTTP requests

const API_PREFIX = "/api";

// creating a custom Axios instance.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || API_PREFIX,

  withCredentials: true, //Include cookies when making requests

  timeout: 15000, // Don't wait forever for the backend
});

export function getErrorMessage(error) {

  const status = error.response?.status; // ?. -> If response exists, get status otherwise don't crash
  const rawDetail = error.response?.data?.detail;

  // FastAPI validation errors (422) return detail as an ARRAY of objects
  // like { msg: "value is not a valid email..." } — flatten it to one
  // friendly string instead of trying to render objects in the UI.
  if (status === 422) {
    if (Array.isArray(rawDetail) && rawDetail.length > 0) {
      const first = rawDetail[0]?.msg || "";
      if (/email/i.test(first)) {
        return "Please enter a valid email address."
      }
      return first || "Please check the form and try again.";
    }
    return rawDetail || "Please check the form and try again.";
  }

  const detail = typeof rawDetail === "string" ? rawDetail : undefined;

  if (status === 400) return detail || "Invalid request. Please check your input.";

  if (status === 401) return detail || "Your session has expired. Please log in again.";

  if (status === 403) return detail || "You don't have permission to do this.";

  if (status === 404) return detail || "Not found.";

  if (status === 409) return detail || "That request is still being processed. Please wait a moment.";

  if (status === 429) return "Too many requests. Please wait a moment and try again.";

  if (status === 503) return detail || "Service temporarily unavailable. Please try again shortly.";

  if (status >= 500) return "Something went wrong. Please try again later.";

  if (error.code === "ECONNABORTED") return "The request timed out. Please try again.";
  if (!error.response) return "Unable to connect to PayCore. Please check your connection.";

  return detail || "Something went wrong. Please try again.";
}

// to avoid refresh storm of the access token
let isRefreshing = false;            // Are we currently refreshing the access token? 
let queuedRequests = [];             // an array that stores requests that are waiting for the refresh to finish

// whatever the response is , first inspect, then give to the app 
api.interceptors.response.use(
  // First argument: success , pass the response through untouched.
  (response) => response,

  // Second argument: any error arrives here first.
  async (error) => {

    const originalRequest = error.config; // contains info about the failed request bcz we have to resend this request after resolving error
    const status = error.response?.status; 

    const isAuthRoute = originalRequest.url?.startsWith("/auth/"); //bcz the refresh itself is /auth so will get caught in loop
    if (
      status !== 401 ||
      !originalRequest ||            // safety: malformed error, nothing to replay
      originalRequest._retry ||
      isAuthRoute
    ) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queuedRequests.push({ resolve, reject });
      }).then(() => api(originalRequest)); // replay after refresh succeeds
    }

    originalRequest._retry = true; //dont try again if failed once
    isRefreshing = true; //the first request is refreshed as it passes the previous if , the second will be pushed in the queue 

    try { //We DON'T want the refresh request to go through the same response interceptor so cant use /api
      await axios.post(
        `${api.defaults.baseURL}/auth/refresh`,
        {},
        { withCredentials: true }
      );

      // Success: wake up every request that was waiting in the queue...
      queuedRequests.forEach(({ resolve }) => resolve());
      queuedRequests = [];

      //and replay the original request with the fresh access cookie.
      return api(originalRequest);
    } catch (refreshError) {

      queuedRequests.forEach(({ reject }) => reject(refreshError));
      queuedRequests = [];
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false; // always reset the flag, success or failure
    }
  }
);

export default api;
