/**
 * BottomNavigation.jsx — the mobile version of the sidebar (shows < 900px).
 * Fixed to the bottom of the screen, thumb-friendly, like real wallet apps.
 */
import { Home, Send, History, User } from "lucide-react";
import { NavLink } from "react-router-dom";

const TABS = [
  { to: "/dashboard", label: "Home", icon: Home },
  { to: "/send-money", label: "Send", icon: Send },
  { to: "/transactions", label: "History", icon: History },
  { to: "/profile", label: "Me", icon: User },
];

export default function BottomNavigation() {
  return (
    <nav className="bottom-nav">
      <div className="bottom-nav-inner">
        {TABS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/dashboard"}
            className={({ isActive }) =>
              `bottom-nav-item${isActive ? " active" : ""}`
            }
          >
            <span className="bn-icon">
              <Icon size={20} />
            </span>
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
