/**
 * Profile.jsx — account information + logout.
 *
 * Deliberately simple: the backend has no "change password" or "edit
 * profile picture" endpoints, so we show none. Honest UI > invented UI.
 */
import { useState } from "react";
import { Mail, AtSign, Phone, Calendar, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { formatDate } from "../utils/formatDate";

export default function Profile() {
  // The user object ALREADY lives in context (fetched at login/boot) —
  // no extra API call needed here. Context doing its job.
  const { user, logout } = useAuth();
  const [loggingOut, setLoggingOut] = useState(false);

  async function handleLogout() {
    setLoggingOut(true);
    await logout(); // AuthContext clears the user → ProtectedRoute
    // redirects to /login automatically. No navigate() needed!
  }

  // Guard: user is always set here (ProtectedRoute guarantees it), but
  // defensive code avoids a crash during odd render timing.
  if (!user) return null;

  const fullName = `${user.first_name} ${user.last_name}`.trim() || user.username;
  const initial = (user.first_name || user.username || "U").charAt(0).toUpperCase();

  return (
    <div>
      <div className="page-header">
        <h1>Profile</h1>
        <p>Your PayCore account details</p>
      </div>

      {/* Identity header */}
      <div className="profile-head">
        <span className="avatar avatar-lg">{initial}</span>
        <div>
          <h1>{fullName}</h1>
          <p>@{user.username}</p>
        </div>
      </div>

      <div className="card card-pad">
        <h2 className="section-title" style={{ marginBottom: 8 }}>
          Account Information
        </h2>

        <div className="review-row">
          <span className="k">
            <Mail size={14} style={{ verticalAlign: "-2px", marginRight: 6 }} />
            Email
          </span>
          <span className="v">{user.email}</span>
        </div>
        <div className="review-row">
          <span className="k">
            <AtSign size={14} style={{ verticalAlign: "-2px", marginRight: 6 }} />
            Username
          </span>
          <span className="v">@{user.username}</span>
        </div>
        <div className="review-row">
          <span className="k">
            <Phone size={14} style={{ verticalAlign: "-2px", marginRight: 6 }} />
            Phone
          </span>
          <span className="v">{user.phone || "Not provided"}</span>
        </div>
        <div className="review-row">
          <span className="k">
            <Calendar size={14} style={{ verticalAlign: "-2px", marginRight: 6 }} />
            Member since
          </span>
          <span className="v">{formatDate(user.created_at)}</span>
        </div>
        <div className="review-row">
          <span className="k">Account status</span>
          <span className="v" style={{ textTransform: "capitalize" }}>
            {user.status}
          </span>
        </div>
      </div>

      <div style={{ marginTop: 24 }}>
        <button
          className="btn btn-danger btn-block"
          style={{ maxWidth: 480 }}
          onClick={handleLogout}
          disabled={loggingOut}
        >
          <LogOut size={17} />
          {loggingOut ? "Logging out..." : "Logout"}
        </button>
      </div>
    </div>
  );
}
