/**
 * AuthContext.jsx — the app's memory of "who is logged in?"
 * ─────────────────────────────────────────────────────────────────────────
 * WHAT THIS FILE IS:
 *   A React Context that holds the logged-in user object and exposes
 *   three actions: login(), register(), logout(). Any component in the
 *   tree can read the user with the useAuth() helper below.
 *
 * WHY WE CREATED IT:
 *   The Dashboard greets the user by name, the Profile shows their email,
 *   the Sidebar shows their initial... Without context, we would fetch
 *   /users/me separately in every one of those components. Instead, we
 *   fetch ONCE and share the result. Context = data every screen needs.
 *
 * REACT CONCEPT — Context API:
 *   Normal props flow parent → child. Context lets a value "teleport"
 *   to any component, no matter how deep, without prop drilling.
 *
 * ─── How authentication works in THIS app (important!) ────────────────────
 *   The backend uses HttpOnly cookies — tiny tokens the browser stores and
 *   attaches to every request automatically, but which JavaScript can NOT
 *   read. That means:
 *     • We never see or store the token ourselves (great for security).
 *     • "Is there a session?" cannot be answered from localStorage.
 *   So on page refresh we simply ASK the backend with GET /users/me:
 *     200 → a valid session exists, we get the profile.
 *     401 → no session (or expired); after a failed /auth/refresh the
 *           interceptor gives up and we show the login page.
 *   This "ask the server" pattern is the only honest way with cookies.
 * ─────────────────────────────────────────────────────────────────────────
 */
import { createContext, useContext, useEffect, useState } from "react";
import { getMyProfile } from "../api/userApi";
import { loginUser, registerUser, logoutUser } from "../api/authApi";
import { getErrorMessage } from "../api/api";

// createContext makes a "channel". Whatever value we give the <Provider>
// below is readable by every descendant via useContext(AuthContext).
const AuthContext = createContext(null);

/**
 * useAuth — a tiny helper so components can write `const { user } = useAuth()`
 * instead of importing useContext + AuthContext everywhere.
 * (A one-function custom hook — deliberately small.)
 */
export function useAuth() {
  return useContext(AuthContext);
}

/**
 * AuthProvider — wraps the whole app (see App.jsx). It owns the user
 * state and the auth actions, and hands them down through the context.
 */
export function AuthProvider({ children }) {
  // `user` is null = "not logged in", an object = "logged in as ...".
  // `booting` = "we are still asking the backend if a session exists".
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(true);

  // useEffect runs AFTER the component renders. With an empty dependency
  // array [] it runs exactly once — like "when the app starts, do this".
  // Perfect place for the session bootstrap check described above.
  useEffect(() => {
    async function checkSession() {
      try {
        // If a valid cookie exists, this returns the profile.
        const response = await getMyProfile();
        setUser(response.data);
      } catch {
        // 401 (no/expired session, refresh already failed) or backend
        // down — either way, treat as "not logged in". The app will show
        // the login page; if the backend is down, pages show errors.
        setUser(null);
      } finally {
        // Whatever happened, we are done deciding → render the app.
        // `finally` runs on both success and failure paths.
        setBooting(false);
      }
    }
    checkSession();
  }, []);

  /**
   * Try to log in. Returns { ok, error } so the Login page can show a
   * message without try/catch gymnastics in the component.
   */
  async function login(email, password) {
    try {
      await loginUser(email, password);
      // Cookies are now set by the browser. Fetch the profile so the
      // context is filled before the dashboard renders.
      const response = await getMyProfile();
      setUser(response.data);
      return { ok: true };
    } catch (error) {
      return { ok: false, error: getErrorMessage(error) };
    }
  }

  /** Create an account, then behave exactly like login(). */
  async function register(formData) {
    try {
      await registerUser(formData);
      return { ok: true };
    } catch (error) {
      return { ok: false, error: getErrorMessage(error) };
    }
  }

  /** Revoke the session on the backend, then wipe local state. */
  async function logout() {
    try {
      await logoutUser(); // backend clears the cookies
    } catch {
      // Even if the backend call fails (offline?), we still clear the
      // local user so the UI returns to the login page.
    } finally {
      setUser(null);
    }
  }

  // The value every child receives. Including the actions means any
  // component can call useAuth().login(...) directly.
  const value = { user, booting, login, register, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
