/**
 * Navbar.jsx — the horizontal bar at the top of every authenticated page.
 * Shows the current page's title (via useLocation) and quick actions.
 */
import { Bell } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Maps a URL path to the title shown in the topbar.
const TITLES = {
  "/dashboard": "Dashboard",
  "/send-money": "Send Money",
  "/transactions": "Transactions",
  "/profile": "Profile",
};

export default function Navbar() {
  const { user } = useAuth();
  const location = useLocation();

  // useLocation() re-renders this component on every navigation, so the
  // title always matches the current page. Transactions/:id has a dynamic
  // path, so we handle it with startsWith.
  let title = TITLES[location.pathname];
  if (!title && location.pathname.startsWith("/transactions/")) {
    title = "Transaction Details";
  }

  // First letter of the user's name → the avatar circle.
  const initial = (user?.first_name || user?.username || "U").charAt(0).toUpperCase();

  return (
    <header className="topbar">
      <h1 className="topbar-title">{title}</h1>

      <div className="topbar-actions">
        {/* Decorative bell for now — real notifications would need a
            backend endpoint, which does not exist yet. */}
        <button className="icon-btn" aria-label="Notifications">
          <Bell size={18} />
          <span className="dot" />
        </button>

        <Link to="/profile" aria-label="Your profile">
          <span className="avatar">{initial}</span>
        </Link>
      </div>
    </header>
  );
}
