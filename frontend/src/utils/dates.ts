/** Today's date as YYYY-MM-DD in the browser's local timezone.
 *
 * `new Date().toISOString()` converts to UTC first, which gives the wrong
 * date for part of the day in any UTC+ timezone (e.g. the UK during BST,
 * UTC+1) - just after midnight local time is still the previous day in UTC.
 * Use this instead of toISOString().slice(0, 10) for "today" as a date input
 * default.
 */
export function todayLocalISODate(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
