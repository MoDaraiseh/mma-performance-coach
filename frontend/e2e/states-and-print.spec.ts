import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";
import { evidence, navigate, noOverflow, seedDemo } from "./helpers";

test("loading and backend failure are announced instead of silently showing a new account", async ({
  page,
}) => {
  let release!: () => void;
  const gate = new Promise<void>((resolve) => (release = resolve));
  await page.route("**/api/auth/session", async (route) => {
    await gate;
    await route.fulfill({
      status: 503,
      json: { error: "QA service temporarily unavailable" },
    });
  });
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText(
    "Loading your training workspace",
  );
  release();
  await expect(page.getByRole("alert")).toContainText(
    "QA service temporarily unavailable",
  );
});

test("workout errors stay readable inside the modal and can be retried", async ({
  page,
}) => {
  await seedDemo(page);
  await navigate(page, "Training");
  await page.getByRole("button", { name: "View session" }).first().click();
  const dialog = page.getByRole("dialog");
  await page.route("**/api/training-sessions", async (route) => {
    if (route.request().method() === "POST")
      await route.fulfill({
        status: 503,
        json: { error: "QA save interrupted; retry your workout." },
      });
    else await route.continue();
  });
  await page.getByRole("button", { name: "Save workout" }).click();
  await expect(dialog.getByRole("alert")).toContainText("QA save interrupted");
  await expect(dialog).toBeVisible();
  await page.unroute("**/api/training-sessions");
  await page.getByRole("button", { name: "Save workout" }).click();
  await expect(dialog).toHaveCount(0);
});

test("onboarding errors, draft restore, validation and modal accessibility", async ({
  page,
}, info) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Build my athlete profile" }).click();
  const dialog = page.getByRole("dialog");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await expect(page.getByLabel("Name", { exact: true })).toBeFocused();
  await page.getByLabel("Name", { exact: true }).fill("Casey QA");
  await page.getByRole("button", { name: "Save progress" }).click();
  await expect(page.getByText("Draft saved")).toBeVisible();
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Build my athlete profile" }).click();
  await expect(page.getByLabel("Name", { exact: true })).toHaveValue(
    "Casey QA",
  );
  await noOverflow(page);
  const scan = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
    .analyze();
  expect(scan.violations).toEqual([]);
  // Recovery credentials are intentionally hidden before any saved screenshot.
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Dismiss recovery token" }).click();
  await page.getByRole("button", { name: "Build my athlete profile" }).click();
  await evidence(page, info, "assessment-modal");
  await page.route("**/api/profile", (route) =>
    route.fulfill({
      status: 422,
      json: { error: "QA invalid profile: review measurements" },
    }),
  );
  await page.getByRole("button", { name: "Go to step 6" }).click();
  await page.getByRole("button", { name: "Save athlete profile" }).click();
  await expect(dialog.getByRole("alert")).toContainText("review measurements");
});

test("mobile drawer is hidden when closed, traps focus, closes with Escape, and has touch targets", async ({
  page,
}) => {
  test.skip(
    (page.viewportSize()?.width || 0) > 700,
    "Mobile drawer is tested at the two requested mobile widths.",
  );
  await seedDemo(page);
  const menu = page.getByRole("button", { name: "Toggle navigation" });
  const sidebar = page.locator(".sidebar");
  await expect(
    sidebar.getByRole("button", { name: "Training", exact: true }),
  ).toBeHidden();
  await expect(menu).toHaveAttribute("aria-expanded", "false");
  await menu.click();
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await expect(sidebar).toHaveAttribute("aria-modal", "true");
  await page.keyboard.press("Escape");
  await expect(menu).toBeFocused();
  await expect(sidebar).toBeHidden();
  const buttons = await page.locator("button:visible").evaluateAll((elements) =>
    elements
      .map((e) => ({
        name: e.textContent || e.getAttribute("aria-label"),
        height: e.getBoundingClientRect().height,
        width: e.getBoundingClientRect().width,
      }))
      .filter((e) => e.height < 44 || e.width < 24),
  );
  expect(buttons).toEqual([]);
});

test("printed reports preserve comparison data, nutrition ingredients and schedule content", async ({
  page,
}, info) => {
  test.skip(
    info.project.name !== "desktop-1440",
    "A4 print uses one fixed paper layout, independently of the screen viewport.",
  );
  await seedDemo(page);
  await page.setViewportSize({ width: 794, height: 1123 });
  for (const [view, required] of [
    ["Overview", "Your athlete profile"],
    ["Training", "Week 1"],
    ["Nutrition", "Your seven-day meal template"],
    ["Comparison lab", "Max Holloway"],
    ["Progress", "Athletic development dashboard"],
  ]) {
    if (view === "Progress") {
      for (const [days, value] of [
        [28, 40],
        [14, 45],
        [0, 50],
      ]) {
        const date = new Date();
        date.setDate(date.getDate() - days);
        expect(
          (
            await page.request.post("/api/progress", {
              data: {
                date: date.toISOString().slice(0, 10),
                weight_kg: 80,
                sleep: 8,
                fatigue: 3,
                benchmarks: [
                  {
                    name: "Bench press",
                    value,
                    unit: "kg",
                    reps: 5,
                    effort: 7,
                    provenance: "measured",
                  },
                ],
              },
            })
          ).ok(),
        ).toBeTruthy();
      }
    }
    if (view === "Progress") await page.reload();
    await navigate(page, view);
    if (view === "Progress") {
      await expect(page.locator(".athlete-analytics")).toContainText(
        "3 of 3 recorded events analyzed",
      );
      await expect(page.locator(".athlete-analytics")).not.toContainText(
        "Loading history",
      );
    }
    await expect(
      page.getByRole("button", { name: "Print report" }),
    ).toBeVisible();
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    await page.emulateMedia({ media: "print" });
    await noOverflow(page);
    await expect(page.locator("main")).toContainText(required);
    if (view === "Comparison lab")
      await expect(page.locator(".match-select").first()).toBeVisible();
    if (view === "Nutrition")
      await expect(page.getByText(/chicken breast/).first()).toBeVisible();
    const filename = `${view.toLowerCase().replaceAll(" ", "-")}-a4.pdf`;
    const pdf = await page.pdf({
      path: path.resolve(
        process.env.PW_EVIDENCE_DIR || "../docs/evidence/phase1",
        filename,
      ),
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
    });
    expect(pdf.byteLength).toBeGreaterThan(10_000);
    await info.attach(filename, { body: pdf, contentType: "application/pdf" });
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    await evidence(
      page,
      info,
      `${view.toLowerCase().replaceAll(" ", "-")}-print`,
    );
    await page.evaluate(() => window.dispatchEvent(new Event("afterprint")));
    await page.emulateMedia({ media: "screen" });
  }
});
