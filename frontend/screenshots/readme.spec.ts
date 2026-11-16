import { expect, Page, test } from "@playwright/test";
import path from "node:path";
import { navigate } from "../e2e/helpers";

// Demo account only. The one-time recovery token is read, dismissed, and then
// checked to be absent from the page before every capture. Run from frontend/.
const out = (name: string) => path.resolve("../docs/images", `${name}.png`);

async function capture(page: Page, token: string, name: string) {
  await expect(page.getByText(/^Loading analytics/)).toHaveCount(0);
  expect(await page.content()).not.toContain(token);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out(name), animations: "disabled" });
}

test("README screenshots", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Explore the demo" }).click();
  const dismiss = page.getByRole("button", { name: "Dismiss recovery token" });
  await expect(dismiss).toBeVisible();
  const token = (await page.locator("code").first().textContent())?.trim();
  expect(token && token.length >= 16).toBeTruthy();
  await dismiss.click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

  await navigate(page, "Settings & data");
  await page.getByRole("button", { name: "Edit assessment" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await capture(page, token!, "assessment");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);

  await navigate(page, "Training");
  await capture(page, token!, "training");
  await navigate(page, "Nutrition");
  await capture(page, token!, "nutrition");
  await navigate(page, "Comparison lab");
  await expect(
    page.getByRole("button", { name: /^Save .+ comparison$/ }).first(),
  ).toBeVisible();
  await expect(
    page.getByText(/^(Updating comparisons|Searching fighter records)/),
  ).toHaveCount(0);
  await capture(page, token!, "comparison");
});
