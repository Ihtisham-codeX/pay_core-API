/**
 * Sidebar.jsx — desktop navigation (hidden below 900px by index.css).
 *
 * NavLink is like Link but knows whether it is the CURRENT route and adds
 * the "active" class automatically — perfect for highlighting the page
 * the user is on. No manual path comparison needed.
 */
import { LayoutDashboard, Send, ArrowLeftRight, User, LogOut } from "lucide-react";
import { NavLink, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Logo from "./Logo";

// One array drives the whole menu: add an entry = new menu item.
const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/send-money", label: "Send Money", icon: Send },
  { to: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { to: "/profile", label: "Profile", icon: User },
];

export default function Sidebar() {
  const { logout } = useAuth();

  return (
    <aside className="sidebar">
      <Link to="/dashboard" className="brand">
        <Logo />
        <span>
          Pay<em>Core</em>
        </span>
      </Link>

      <nav className="sidebar-nav">
        {LINKS.map(({ to, label, icon: Icon }) => (
          // `end` on Dashboard's NavLink means "only active on /dashboard
          // exactly" — otherwise /transactions would also light up when
          // viewing /transactions/123 (they share the prefix).
          <NavLink
            key={to}
            to={to}
            end={to === "/dashboard"}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <Icon size={19} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <button className="logout-btn" onClick={logout}>
          <LogOut size={19} />
          Logout
        </button>
      </div>
    </aside>
  );
}
