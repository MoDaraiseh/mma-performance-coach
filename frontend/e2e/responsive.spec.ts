import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { writeFileSync } from "node:fs";
import path from "node:path";
import { evidence, navigate, noOverflow, pages, seedDemo } from "./helpers";

test("all workspace pages fit viewport and meet automated WCAG checks", async ({
  page,
}, info) => {
  const errors: string[] = [];
  const checks: object[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("response", (r) => {
    if (
      r.status() >= 400 &&
      !(r.url().endsWith("/api/auth/session") && r.status() === 401)
    )
      errors.push(`${r.status()} ${r.url()}`);
  });
  await seedDemo(page);
  for (const name of pages) {
    if (name !== "Overview") await navigate(page, name);
    await noOverflow(page);
    const result = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    checks.push({
      page: name,
      violations: result.violations.map((v) => ({
        id: v.id,
        impact: v.impact,
        targets: v.nodes.map((n) => n.target),
      })),
      documentWidth: await page.evaluate(
        () => document.documentElement.scrollWidth,
      ),
    });
    await info.attach(`${name}-axe`, {
      body: JSON.stringify(result.violations, null, 2),
      contentType: "application/json",
    });
    expect
      .soft(
        result.violations,
        `${name}: ${JSON.stringify(result.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })))}`,
      )
      .toEqual([]);
    await evidence(page, info, name.toLowerCase().replaceAll(" ", "-"));
  }
  expect(errors).toEqual([]);
  writeFileSync(
    path.resolve(
      process.env.PW_EVIDENCE_DIR || "../docs/evidence/phase1",
      `${info.project.name}-checks.json`,
    ),
    JSON.stringify(
      {
        browser: page.context().browser()?.version(),
        viewport: page.viewportSize(),
        checks,
        runtimeErrors: errors,
      },
      null,
      2,
    ),
  );
});

test("keyboard navigation, session modal, focus restoration and reduced motion", async ({
  page,
}) => {
  await seedDemo(page);
  await navigate(page, "Training");
  const opener = page.getByRole("button", { name: "View session" }).first();
  await opener.focus();
  await page.keyboard.press("Enter");
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  const close = page.getByRole("button", { name: "Close session" });
  await expect(close).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(
    page.getByRole("button", { name: "Save workout" }),
  ).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(close).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect(opener).toBeFocused();
  await page.emulateMedia({ reducedMotion: "reduce" });
  expect(
    await page
      .getByRole("button", { name: "Next week" })
      .evaluate((e) => getComputedStyle(e).transitionDuration),
  ).toMatch(/^0s|0.00001s$/);
});
