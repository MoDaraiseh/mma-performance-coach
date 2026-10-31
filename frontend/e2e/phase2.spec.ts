import { expect, test } from "@playwright/test";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("reassessment proposal approval and archived program access", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Training");
  await expect(
    page.getByRole("heading", { name: "Saved program history" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "View session" }).first().click();
  const exercise = await page
    .locator(".session-modal .exercise h3")
    .first()
    .innerText();
  await page
    .getByRole("button", { name: `Add actual set · ${exercise}`, exact: true })
    .click();
  await page
    .getByLabel(`Repetitions · set 1 · ${exercise}`, { exact: true })
    .fill("8");
  await page
    .getByLabel(`Load (kg) · set 1 · ${exercise}`, { exact: true })
    .fill("10");
  await page.getByRole("button", { name: "Save workout" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  const logs = await (await page.request.get("/api/training-sessions")).json();
  expect(logs[0].data.performances[0].sets[0]).toMatchObject({
    reps: 8,
    weight_kg: 10,
  });
  await page.getByRole("button", { name: "View session" }).first().click();
  await page.getByRole("button", { name: "Mark session missed" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Missed", exact: true }),
  ).toBeVisible();
  await navigate(page, "Progress");
  await page.getByRole("button", { name: "Weekly check-in" }).click();
  await page.getByLabel("Sleep (hours)").fill("5");
  await page.getByLabel("Fatigue (1–10)").fill("8");
  await page.getByLabel("Body fat (%)").fill("17");
  await page
    .getByLabel("Mobility", { exact: true })
    .selectOption("Comfortable");
  await page.getByRole("button", { name: "Save check-in" }).click();
  await page.getByRole("button", { name: "Run reassessment" }).click();
  await page
    .getByRole("button", { name: "Preview recommended adjustment" })
    .click();
  await navigate(page, "Training");
  await expect(page.locator(".training-grid")).toHaveCount(0);
  await expect(
    page.getByText(/Training inputs or recovery changed/),
  ).toBeVisible();
  await navigate(page, "Overview");
  await expect(
    page.getByText(/Training inputs or recovery changed/),
  ).toBeVisible();
  await navigate(page, "AI coach");
  await expect(
    page.getByText("4 → 3 days per week", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Approve & apply" }).click();
  await expect(page.getByText("approved", { exact: true })).toBeVisible();
  await navigate(page, "Training");
  const archive = page
    .locator("details")
    .filter({ has: page.locator("summary", { hasText: "Version 1" }) });
  await archive.locator("summary").click();
  await expect(archive).toContainText("Week 12");
  await noOverflow(page);
  await evidence(page, info, "phase2-history");
});
