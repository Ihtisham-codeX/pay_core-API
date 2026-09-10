/**
 * Logo.jsx — the PayCore brand mark, reused on auth pages, sidebar, topbar.
 *
 * A simple rounded square with a stylized "P" — distinct branding, not a
 * copy of any existing wallet app. Keeping it a component means changing
 * the logo once updates every screen.
 */
export default function Logo({ size = 34 }) {
  return (
    <span
      className="brand-logo"
      style={{ width: size, height: size, borderRadius: size * 0.3 }}
      aria-hidden="true"
    >
      <svg
        width={size * 0.62}
        height={size * 0.62}
        viewBox="0 0 24 24"
        fill="none"
      >
        {/* Stylized P + coins stack abstraction */}
        <path
          d="M7 20V5.5A1.5 1.5 0 0 1 8.5 4H13a5 5 0 0 1 0 10H9.4"
          stroke="currentColor"
          strokeWidth="2.6"
          strokeLinecap="round"
        />
        <circle cx="16.4" cy="18.2" r="1.9" fill="currentColor" />
      </svg>
    </span>
  );
}
