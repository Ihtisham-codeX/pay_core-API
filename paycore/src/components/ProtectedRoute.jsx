/**
 * ProtectedRoute.jsx — a doorman for private pages.
 *
 * It wraps the routes that require a session (see App.jsx). Its whole job:
 *   • Still booting?            → show a spinner (don't flash the login page
 *                                 for half a second on every refresh).
 *   • Logged out?               → redirect to /login.
 *   • Logged in?                → render the page the user asked for.
 */
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoadingSpinner from "./LoadingSpinner";

export default function ProtectedRoute({ children }) {
  const { user, booting } = useAuth();

  // While AuthContext is asking the backend "any session?", we can't know
  // yet — show a loading state instead of deciding prematurely.
  if (booting) {
    return <LoadingSpinner fullPage label="Loading PayCore..." />;
  }

  // No user → bounce to login. `replace` means this redirect doesn't pollute
  // the browser history (the back button won't return here).
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Authenticated → render the actual page (children = <Dashboard /> etc).
  return children;
}
