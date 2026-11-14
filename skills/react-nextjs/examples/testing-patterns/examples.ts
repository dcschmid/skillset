// testing-patterns — the two layers that carry the most weight
// (testing.md). Component: behavior+roles via RTL. E2E: real app, real flow.

// __tests__/button.test.tsx — Vitest + RTL: query by role, assert effect.
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "../reusable-components/Button";

describe("Button", () => {
  it("fires onClick and exposes disabled state", async () => {
    const on = vi.fn();
    render(<Button onClick={on}>Save</Button>);
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(on).toHaveBeenCalledOnce();
  });
  it("does not fire when disabled", async () => {
    const on = vi.fn();
    render(<Button disabled onClick={on}>Save</Button>);
    await userEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(on).not.toHaveBeenCalled();
    expect(screen.getByRole("button")).toBeDisabled();
  });
});

// e2e/rename.spec.ts — Playwright (Firefox default): one critical flow,
// locators by role/label, no sleeps. Server Components verified HERE, not by
// unit-importing them (testing.md RSC note).
import { test, expect } from "@playwright/test";

test("rename project round-trip", async ({ page }) => {
  await page.goto("/settings");
  const input = page.getByLabel("Project name");
  await input.fill("Renamed");
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByRole("button", { name: "Save" })).toBeEnabled();
  await page.reload();
  await expect(input).toHaveValue("Renamed"); // invalidation actually worked
});
