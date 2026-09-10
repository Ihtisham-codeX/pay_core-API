/**
 * LoadingSpinner.jsx — shows "something is happening" instead of nothing.
 *
 * Two sizes:
 *   default   → small, fits inside a button ("Sending...")
 *   fullPage  → big, centered in an empty area (dashboard loading)
 */
import "./LoadingSpinner.css";

export default function LoadingSpinner({ fullPage = false, label = "" }) {
  if (fullPage) {
    return (
      <div className="page-loading">
        <div className="spinner spinner-dark" />
        {label && <span>{label}</span>}
      </div>
    );
  }
  return <span className="spinner" aria-label={label || "Loading"} />;
}
