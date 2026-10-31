import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("technical goals, exact availability, approved revision and session-fatigue feedback", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Settings & data");
  await page.getByRole("button", { name: "Edit assessment" }).click();
  await page.getByRole("button", { name: "Go to step 3" }).click();
  await page
    .getByLabel("Technical goals for Boxing")
    .fill("Defensive exits and stance recovery");
  await page.getByRole("button", { name: "Go to step 5" }).click();
  for (const day of ["Tuesday", "Thursday", "Sunday"])
    await page.getByLabel(day, { exact: true }).check();
  await page.getByRole("button", { name: "Go to step 6" }).click();
  await page.getByRole("button", { name: "Save athlete profile" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await navigate(page, "AI coach");
  await page.getByLabel("Available days per week", { exact: true }).fill("3");
  await page
    .getByRole("textbox", { name: "Reason", exact: true })
    .fill("Respect selected weekdays");
  await page
    .getByRole("button", { name: "Preview change", exact: true })
    .click();
  await page.getByRole("button", { name: "Approve & apply" }).click();
  await expect(page.getByText("approved", { exact: true })).toBeVisible();
  await navigate(page, "Training");
  const active = await (await page.request.get("/api/training-plans")).json();
  expect(
    active.data.weeks[0].sessions.map((s: { day: string }) => s.day),
  ).toEqual(["Tuesday", "Thursday", "Sunday"]);
  await expect(
    page.getByRole("heading", { name: "Athlete development model" }),
  ).toBeVisible();
  await page
    .locator("summary")
    .filter({ hasText: /^Boxing: / })
    .click();
  await expect(
    page
      .getByText(/Recorded goals: Defensive exits and stance recovery/)
      .first(),
  ).toBeVisible();
  await noOverflow(page);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await evidence(page, info, "phase7-development");
  await page
    .getByRole("button", { name: "View session", exact: true })
    .first()
    .click();
  await page
    .getByLabel("Post-session fatigue (1–10, optional)", { exact: true })
    .fill("8");
  await page.getByRole("button", { name: "Save workout", exact: true }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(
    page.getByText("High fatigue recorded with a recent performed session", {
      exact: true,
    }),
  ).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-sessions")).json())[0].data
      .fatigue,
  ).toBe(8);
});

test("trained supervised profile sees bounded power and one interval session without weekly escalation", async ({
  page,
}, info) => {
  expect((await page.request.post("/api/auth/register")).ok()).toBeTruthy();
  expect(
    (
      await page.request.put("/api/profile", {
        data: {
          name: "Casey",
          days: 6,
          gym_years: 4,
          current_frequency: 5,
          mobility: "Comfortable",
          strength_coach: true,
          power_practice: true,
          conditioning_mode: "interval_cycling",
          equipment: ["dumbbells", "bike", "medicine_ball"],
        },
      })
    ).ok(),
  ).toBeTruthy();
  expect((await page.request.post("/api/training-plans")).ok()).toBeTruthy();
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Let's get better, Casey." }),
  ).toBeVisible();
  await navigate(page, "Training");
  await page
    .getByRole("button", { name: "View session", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Medicine ball chest pass",
      exact: true,
      level: 3,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close session" }).click();
  await page
    .getByRole("button", { name: "View session", exact: true })
    .nth(2)
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Controlled cycling intervals",
      exact: true,
      level: 3,
    }),
  ).toBeVisible();
  await expect(
    page.getByText(/Three rounds: 1 minute controlled work at RPE 7/),
  ).toBeVisible();
  await noOverflow(page);
  await evidence(page, info, "phase7-intervals");
});
