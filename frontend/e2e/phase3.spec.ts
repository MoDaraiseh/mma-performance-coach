import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import path from "node:path";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("catalog, recorded performance trends and evidence-based future progression", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Training");
  await expect(
    page.getByRole("heading", { name: "Exercise catalog", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Find an exercise").fill("goblet");
  const catalog = page.locator("details").filter({
    has: page.locator("summary", { hasText: "Goblet squat · Strength" }),
  });
  await catalog.locator("summary").click();
  await expect(catalog).toContainText("Common mistakes");
  await expect(catalog).toContainText("dumbbells");
  for (const week of [1, 2]) {
    await page
      .getByLabel("Training week", { exact: true })
      .selectOption(String(week));
    await page
      .getByRole("button", { name: "View session", exact: true })
      .first()
      .click();
    await expect(page.getByLabel("Effort (1–10)", { exact: true })).toHaveValue(
      "",
    );
    await page
      .getByRole("button", {
        name: "Add actual set · Goblet squat",
        exact: true,
      })
      .click();
    await page
      .getByLabel("Repetitions · set 1 · Goblet squat", { exact: true })
      .fill("8");
    await page
      .getByLabel("Load (kg) · set 1 · Goblet squat", { exact: true })
      .fill("10");
    await page
      .getByLabel("Set RPE (1–10) · set 1 · Goblet squat", { exact: true })
      .fill("5");
    await page
      .getByLabel("Exercise notes · Goblet squat", { exact: true })
      .fill("Controlled and comfortable");
    await page.getByLabel("Effort (1–10)", { exact: true }).fill("5");
    await page
      .getByLabel("Session date", { exact: true })
      .fill(
        new Date(Date.now() - (week === 1 ? 7 : 0) * 86400000)
          .toISOString()
          .slice(0, 10),
      );
    await page
      .getByRole("button", { name: "Save workout", exact: true })
      .click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
  }
  await navigate(page, "Progress");
  await page.getByRole("button", { name: "Weekly check-in" }).click();
  await page.getByLabel("Sleep (hours)").fill("8");
  await page.getByLabel("Fatigue (1–10)").fill("3");
  await page.getByLabel("Muscle soreness").fill("2");
  await page.getByLabel("Recovery readiness").fill("4");
  await page.getByRole("button", { name: "Save check-in" }).click();
  await page
    .getByLabel("Recorded exercise", { exact: true })
    .selectOption("Goblet squat");
  await expect(
    page
      .getByRole("table")
      .filter({ has: page.locator("caption", { hasText: "Actual sets" }) }),
  ).toContainText("Controlled and comfortable");
  await page.getByRole("button", { name: "Run reassessment" }).click();
  await page
    .getByRole("button", { name: "Preview recommended adjustment" })
    .click();
  await navigate(page, "AI coach");
  await page
    .getByText("Review full proposed prescription", { exact: true })
    .click();
  await expect(page.getByText(/suggested load 10.25 kg/).first()).toBeVisible();
  await page.getByRole("button", { name: "Approve & apply" }).click();
  await navigate(page, "Training");
  await expect(page.getByLabel("Training week", { exact: true })).toHaveValue(
    "5",
  );
  await expect(
    page.getByRole("heading", { name: "Exercise performance over time" }),
  ).toBeVisible();
  await noOverflow(page);
  await page.locator(".recharts-line-dots .recharts-dot").first().hover();
  await expect(page.locator(".recharts-default-tooltip")).toBeVisible();
  await page
    .locator("section.card")
    .filter({
      has: page.getByRole("heading", {
        name: "Exercise performance over time",
        exact: true,
      }),
    })
    .screenshot({
      path: path.resolve(
        process.env.PW_EVIDENCE_DIR || "../docs/evidence/phase3",
        `${info.project.name}-phase3-performance-panel.png`,
      ),
      animations: "disabled",
    });
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await evidence(page, info, "phase3-progress");
});

test("exercise substitution approval and failed-session recovery review", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Training");
  await page
    .getByRole("button", { name: "View session", exact: true })
    .first()
    .click();
  await page
    .getByText("Exercise substitution", { exact: true })
    .first()
    .click();
  await page
    .getByLabel("Preview alternative for Goblet squat", { exact: true })
    .selectOption("chair-squat");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await navigate(page, "AI coach");
  await expect(
    page.getByText(/replace Goblet squat with Chair squat/).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "Approve & apply" }).click();
  await navigate(page, "Training");
  await page
    .getByRole("button", { name: "View session", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "Chair squat", exact: true, level: 3 }),
  ).toBeVisible();
  await page
    .getByLabel("Session outcome", { exact: true })
    .selectOption("failed");
  await page.getByLabel("Effort (1–10)", { exact: true }).fill("9");
  await page.getByRole("button", { name: "Save workout", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await navigate(page, "Progress");
  await page.getByRole("button", { name: "Weekly check-in" }).click();
  await page.getByLabel("Muscle soreness").fill("8");
  await page.getByLabel("Recovery readiness").fill("1");
  await page.getByRole("button", { name: "Save check-in" }).click();
  await expect(
    page.getByText(/High reported muscle soreness; Low reported readiness/),
  ).toBeVisible();
  await page
    .getByLabel("Reassessment checkpoint", { exact: true })
    .selectOption("12");
  await page.getByRole("button", { name: "Run reassessment" }).click();
  await expect(
    page.getByRole("button", { name: "Preview recommended adjustment" }),
  ).toBeDisabled();
  await noOverflow(page);
  await evidence(page, info, "phase3-recovery");
});
