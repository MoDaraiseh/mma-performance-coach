import { expect, Page, TestInfo } from "@playwright/test";
import path from "node:path";

export const pages = [
  "Overview",
  "Physical analysis",
  "Fighting style",
  "Comparison lab",
  "Training",
  "Nutrition",
  "Progress",
  "AI coach",
] as const;
export async function seedDemo(page: Page) {
  expect((await page.request.post("/api/auth/register")).ok()).toBeTruthy();
  expect((await page.request.post("/api/demo")).ok()).toBeTruthy();
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
}
export async function navigate(page: Page, name: string) {
  const menu = page.getByRole("button", { name: "Toggle navigation" });
  if (
    (await menu.isVisible()) &&
    !(await page
      .locator(".sidebar")
      .getByRole("button", { name, exact: true })
      .isVisible())
  )
    await menu.click();
  await page
    .locator(".sidebar")
    .getByRole("button", { name, exact: true })
    .click();
  await expect(page.locator(".breadcrumb strong")).toHaveText(
    name === "Settings & data" ? "Settings" : name,
  );
  await expect(
    page.getByText("Loading analytics…", { exact: true }),
  ).toHaveCount(0);
  await page.evaluate(() => document.fonts.ready);
}
export async function noOverflow(page: Page) {
  const requestedWidth = page.viewportSize()?.width;
  const overflow = await page.evaluate(() => ({
    width: innerWidth,
    document: document.documentElement.scrollWidth,
    offenders: [...document.querySelectorAll("main *")]
      .filter((el) => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && (r.right > innerWidth + 1 || r.left < -1);
      })
      .slice(0, 8)
      .map((e) => ({
        tag: e.tagName,
        class: e.className,
        text: e.textContent?.slice(0, 50),
      })),
  }));
  expect(overflow.document, JSON.stringify(overflow)).toBeLessThanOrEqual(
    (requestedWidth ?? overflow.width) + 1,
  );
}
export async function evidence(page: Page, info: TestInfo, name: string) {
  const file = path.resolve(
    process.env.PW_EVIDENCE_DIR || "../docs/evidence/phase1",
    `${info.project.name}-${name}.png`,
  );
  await page.screenshot({ path: file, fullPage: true, animations: "disabled" });
  await info.attach(name, { path: file, contentType: "image/png" });
}
