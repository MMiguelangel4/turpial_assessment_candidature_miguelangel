import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import LoanList from "../components/LoanList.vue";

// Stub the API module so the component test doesn't need a running backend.
vi.mock("../api/loans", () => ({
  listLoans: vi.fn(async () => [
    {
      id: 1,
      borrower: "Rosa Delgado",
      principal: "10000.00",
      annual_rate: "0.1200",
      fees: "150.00",
      opened_on: "2026-01-05",
      outstanding: "10150.00",
    },
  ]),
}));

const stubs = { RouterLink: { template: "<a><slot /></a>" } };

afterEach(() => vi.clearAllMocks());

describe("LoanList", () => {
  it("renders a row per loan once loaded", async () => {
    const wrapper = mount(LoanList, { global: { stubs } });
    await flushPromises();
    expect(wrapper.findAll("tbody tr")).toHaveLength(1);
    expect(wrapper.text()).toContain("Rosa Delgado");
  });
});
