/**
 * formatCurrency — turns a number into Pakistani Rupee text.
 *
 * Why a separate file? Formatting rules (the "Rs." prefix, comma grouping,
 * two decimal places) must look IDENTICAL on every screen. If we copied the
 * logic into each component, fixing one screen would mean finding them all.
 * One function = one place to change. This is called "separation of concerns".
 *
 * Examples:
 *   formatCurrency(125450)      → "Rs. 125,450.00"
 *   formatCurrency(2500.5)      → "Rs. 2,500.50"
 *   formatCurrency(-1200)       → "Rs. 1,200.00"   (sign handled by the caller)
 */
export function formatCurrency(amount) {
  // Number(...) converts whatever we received ("2500", 2500, undefined...)
  // into a proper number so the formatter never crashes.
  const value = Number(amount);

  // Math.abs removes the minus sign. Components decide themselves whether to
  // show "+"/"−" based on the transaction type — the formatter only formats.
  const safeValue = Number.isNaN(value) ? 0 : Math.abs(value);

  // Intl.NumberFormat is built into JavaScript. "en-US" gives us the
  // grouping style used in Pakistan's banking apps: 1,250,000.00
  const formatted = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(safeValue);

  return `Rs. ${formatted}`;
}
