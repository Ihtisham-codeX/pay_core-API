/**
 * Register.jsx — create a PayCore account.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • One state OBJECT — instead of six separate useState calls, all form
 *     fields live in one object and we update one key at a time with the
 *     spread operator: { ...form, email: newValue }. Same idea as Login,
 *     just scaled up — learn both styles and pick what reads clearer.
 *   • Client-side validation BEFORE the network call — instant feedback,
 *     zero waiting. The backend re-checks everything (real security).
 *   • Field-level errors dict — { email: "Required" } lets us paint the
 *     exact input that is wrong, not just a generic banner.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import Logo from "../components/Logo";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Register() {
  const navigate = useNavigate();
  const { register } = useAuth();

  // The whole form in one object. useState initializes every key.
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [fieldErrors, setFieldErrors] = useState({}); // { email: "..." }
  const [error, setError] = useState("");             // banner message
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // One generic onChange for every field, thanks to computed keys:
  // setForm({ ...form, [name]: value }) merges the new value into the old
  // object without touching the other fields.
  function handleChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  }

  // Front-end validation mirrors the backend's Pydantic rules
  // (src/schemas/auth.py) so users get instant, specific feedback.
  // Returns an object of errors; {} = all good.
  function validate() {
    const errors = {};

    if (!form.firstName.trim()) errors.firstName = "First name is required.";
    if (!form.lastName.trim()) errors.lastName = "Last name is required.";

    if (!/^[a-zA-Z0-9_]{3,30}$/.test(form.username)) {
      errors.username =
        "Username must be 3–30 characters, letters/numbers/underscores only.";
    }

    // Simple shape check — the EmailStr validator on the backend is stricter.
    if (!/^\S+@\S+\.\S+$/.test(form.email)) {
      errors.email = "Please enter a valid email address.";
    }

    if (form.password.length < 8) {
      errors.password = "Password must be at least 8 characters.";
    }

    if (form.password !== form.confirmPassword) {
      errors.confirmPassword = "Passwords do not match.";
    }

    return errors;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const errors = validate();
    setFieldErrors(errors);

    // Object.keys(errors).length === 0 → the errors object is empty.
    if (Object.keys(errors).length > 0) return; // stay on the form

    setLoading(true);
    const result = await register({
      email: form.email.trim(),
      username: form.username.trim(),
      password: form.password,
      firstName: form.firstName.trim(),
      lastName: form.lastName.trim(),
      // No phone field in this form — authApi sends null for us.
    });
    setLoading(false);

    if (result.ok) {
      // Registration succeeded → let the user log in with their new
      // credentials (the backend issues no token at register time).
      navigate("/login", { replace: true });
    } else {
      // e.g. "Email or username already registered."
      setError(result.error);
    }
  }

  // Small helper so each field shows its error consistently.
  const err = (name) =>
    fieldErrors[name] ? <p className="field-error">{fieldErrors[name]}</p> : null;

  return (
    <div className="auth-page">
      <div className="card auth-card">
        <div className="auth-brand">
          <Logo size={48} />
          <h1>Create your account</h1>
          <p>Join PayCore in less than a minute</p>
        </div>

        {error && (
          <div className="alert alert-error" role="alert">
            <AlertCircle size={17} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {/* Two name fields share one row via CSS grid (.form-row) */}
          <div className="form-row">
            <div className="field">
              <label htmlFor="firstName">First name</label>
              <input
                id="firstName"
                name="firstName"
                className="input"
                placeholder="Ali"
                value={form.firstName}
                onChange={handleChange}
              />
              {err("firstName")}
            </div>
            <div className="field">
              <label htmlFor="lastName">Last name</label>
              <input
                id="lastName"
                name="lastName"
                className="input"
                placeholder="Khan"
                value={form.lastName}
                onChange={handleChange}
              />
              {err("lastName")}
            </div>
          </div>

          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              name="username"
              className="input"
              placeholder="ali_khan"
              value={form.username}
              onChange={handleChange}
              autoComplete="username"
            />
            {err("username")}
          </div>

          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              className="input"
              placeholder="you@example.com"
              value={form.email}
              onChange={handleChange}
              autoComplete="email"
            />
            {err("email")}
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <div className="input-wrap">
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                className="input"
                placeholder="At least 8 characters"
                value={form.password}
                onChange={handleChange}
                autoComplete="new-password"
              />
              <button
                type="button"
                className="eye-btn"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {err("password")}
          </div>

          <div className="field">
            <label htmlFor="confirmPassword">Confirm password</label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type={showPassword ? "text" : "password"}
              className="input"
              placeholder="Repeat your password"
              value={form.confirmPassword}
              onChange={handleChange}
              autoComplete="new-password"
            />
            {err("confirmPassword")}
          </div>

          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? (
              <>
                <LoadingSpinner /> Creating account...
              </>
            ) : (
              "Register"
            )}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
