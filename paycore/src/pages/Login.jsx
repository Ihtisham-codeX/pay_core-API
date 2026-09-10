/**
 * Login.jsx — the door into PayCore.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • Controlled inputs — the <input> value lives in React state and every
 *     keystroke updates that state (onChange). React state is the single
 *     source of truth; the DOM just mirrors it.
 *   • Conditional rendering — {error && <div>} shows the alert only when
 *     there IS an error. `false && x` renders nothing.
 *   • useNavigate — a hook from React Router that lets us redirect
 *     programmatically after login succeeds.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import Logo from "../components/Logo";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth(); // login() comes from AuthContext

  // One state per piece of information. Simple and beginner-friendly.
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");      // server/validation message
  const [loading, setLoading] = useState(false); // spinner inside the button

  // Runs when the form is submitted. `e.preventDefault()` stops the
  // browser's default full-page reload — we handle it the React way.
  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    // Client-side checks are for UX (instant feedback). The backend
    // validates everything again — never trust the browser.
    if (!email.trim() || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true); // disable the button so it can't be double-clicked
    const result = await login(email.trim(), password);
    setLoading(false);

    if (result.ok) {
      // navigate("/dashboard") sends the user onward. `replace` avoids a
      // dead login page in the back-button history.
      navigate("/dashboard", { replace: true });
    } else {
      setError(result.error); // e.g. "Invalid email or password."
    }
  }

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <div className="auth-brand">
          <Logo size={48} />
          <h1>Welcome to PayCore</h1>
          <p>Log in to access your wallet</p>
        </div>

        {/* Conditional render: only mount the alert when error is set */}
        {error && (
          <div className="alert alert-error" role="alert">
            <AlertCircle size={17} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="email">Email</label>
            {/* Controlled input: value + onChange. Reading them together
                is THE fundamental React form pattern. */}
            <input
              id="email"
              type="email"
              className="input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              autoFocus
            />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <div className="input-wrap">
              <input
                id="password"
                // type flips between text/password — that is the whole
                // "show password" trick.
                type={showPassword ? "text" : "password"}
                className="input"
                placeholder="Your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <button
                type="button" // "button" so it does NOT submit the form
                className="eye-btn"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? (
              <>
                <LoadingSpinner /> Logging in...
              </>
            ) : (
              "Login"
            )}
          </button>
        </form>

        <p className="auth-switch">
          New to PayCore? <Link to="/register">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
