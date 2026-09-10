/**
 * NotFound.jsx — the catch-all route (path="*").
 *
 * Any URL the router does not recognize lands here. Even a fintech app
 * should handle wrong addresses gracefully.
 */
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="auth-page">
      <div className="card auth-card" style={{ textAlign: "center" }}>
        <div style={{ fontSize: 42, fontWeight: 800, color: "var(--primary)" }}>
          404
        </div>
        <h1 style={{ fontSize: 20, marginBottom: 6 }}>Page not found</h1>
        <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 20 }}>
          The page you're looking for doesn't exist or has moved.
        </p>
        <Link to="/dashboard" className="btn btn-primary btn-block">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
