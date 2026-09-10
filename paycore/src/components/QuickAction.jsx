/**
 * QuickAction.jsx — one tile in the dashboard's quick actions grid.
 *
 * Can be a link (when `to` is given) or a disabled placeholder (for future
 * features like Add Money / Pay Bills that the backend does not support
 * yet). A `disabled` button communicates "coming soon" honestly.
 */
import { Link } from "react-router-dom";

export default function QuickAction({ to, icon: Icon, label, disabled = false }) {
  if (disabled) {
    return (
      <button className="quick-action" disabled title="Coming soon">
        <span className="qa-icon">
          <Icon size={21} />
        </span>
        {label}
      </button>
    );
  }

  return (
    <Link to={to} className="quick-action">
      <span className="qa-icon">
        <Icon size={21} />
      </span>
      {label}
    </Link>
  );
}
