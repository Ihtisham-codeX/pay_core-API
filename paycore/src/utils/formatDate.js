/**
 * formatDate — shared date helpers.
 *
 * The backend sends dates as ISO strings like "2026-09-08T14:23:45".
 * We never print that raw string to users — banking apps show friendly
 * dates. These three helpers cover every date the UI needs.
 */

/**
 * "2026-09-08T14:23:45" → "08 September 2026"
 * Used on the transaction details (receipt) page.
 */
export function formatDate(dateString) {
  const date = new Date(dateString); // Date parses ISO strings automatically
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

/**
 * "2026-09-08T14:23:45" → "08 Sep 2026, 2:45 PM"
 * Used where both date and time matter (transactions list).
 */
export function formatDateTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

/**
 * Returns the group heading for a transaction date:
 * today → "Today", yesterday → "Yesterday", otherwise a full date.
 *
 * The transactions page calls this while building its date groups.
 */
export function dateGroupLabel(dateString) {
  const date = new Date(dateString);

  // Build "YYYY-MM-DD" for the date we are labeling, today, and yesterday.
  // Comparing strings like this is simpler than comparing time math.
  const toKey = (d) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(
      d.getDate()
    ).padStart(2, "0")}`;

  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1); // move back one day

  if (toKey(date) === toKey(today)) return "Today";
  if (toKey(date) === toKey(yesterday)) return "Yesterday";
  return formatDate(dateString);
}
