/**
 * Display helpers for money values.
 *
 * The API sends amounts as strings to avoid float rounding (see GLOSSARY.md
 * §Money and rounding). Keep them as strings until the moment they're displayed.
 */

/** Format an amount string for display: "1234.5" -> "1,234.50". */
export function formatMoney(value: string | number): string {
  const n = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(n)) return "—";
  return n.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/** Format a signed amount, keeping the sign visible: "-12.5" -> "-12.50". */
export function formatSigned(value: string | number): string {
  const n = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return sign + formatMoney(n);
}
