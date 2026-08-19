import { describe, expect, it } from "vitest";
import { formatMoney, formatSigned } from "../money";

describe("formatMoney", () => {
  it("always shows two decimal places", () => {
    expect(formatMoney("1234.5")).toBe("1,234.50");
  });

  it("handles a plain integer string", () => {
    expect(formatMoney("4000")).toBe("4,000.00");
  });

  it("returns a dash for a non-numeric value", () => {
    expect(formatMoney("not a number")).toBe("—");
  });
});

describe("formatSigned", () => {
  it("keeps a positive sign visible", () => {
    expect(formatSigned("12.5")).toBe("+12.50");
  });

  it("keeps the negative sign", () => {
    expect(formatSigned("-12.5")).toBe("-12.50");
  });
});
