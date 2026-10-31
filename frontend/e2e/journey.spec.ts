import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { navigate, noOverflow, seedDemo } from "./helpers";

test("complete athlete journey through onboarding, logging, reassessment, approvals and export", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Build my athlete profile" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await page.getByLabel("Name", { exact: true }).fill("Jordan QA");
  await page.getByLabel("Age", { exact: true }).fill("29");
  await page
    .getByLabel("Metabolic equation input (optional)")
    .selectOption("male");
  await page.getByLabel("Height (cm)").fill("181");
  await page.getByLabel("Everyday weight (kg)").fill("79");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page.getByLabel(/Total wingspan/).fill("186");
  await page.getByRole("button", { name: "Save progress" }).click();
  await expect(page.getByText("Draft saved")).toBeVisible();
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await dialog.getByRole("button", { name: "Boxing", exact: true }).click();
  await page.getByLabel("Experience level").selectOption("Novice");
  await page.getByLabel("Months practiced").fill("18");
  await page.getByLabel("Sessions / week").fill("2");
  await page.getByLabel("Instructor access").check();
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page.getByLabel("Years of strength training").fill("2");
  await page.getByRole("button", { name: "Add result" }).click();
  await page.getByLabel("Result (kg)").fill("60");
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page.getByLabel("Available training days per week").fill("4");
  await page.getByLabel("Maximum daily training minutes").fill("60");
  await dialog.getByRole("button", { name: "Halal", exact: true }).click();
  await page.getByRole("button", { name: "Continue", exact: true }).click();
  await page
    .getByLabel("Primary development goal")
    .selectOption("Develop MMA skills");
  await page.getByRole("button", { name: "Save athlete profile" }).click();
  await expect(dialog).toHaveCount(0);
  await page.getByRole("button", { name: "Dismiss recovery token" }).click();
  await expect(
    page.getByRole("heading", { name: /Jordan/, level: 1 }),
  ).toBeVisible();
  await navigate(page, "Physical analysis");
  await expect(page.locator(".division-big")).toHaveText("Middleweight");
  await navigate(page, "Comparison lab");
  await expect(
    page.getByRole("button", { name: "Save Max Holloway comparison" }),
  ).toBeVisible();
  await page.getByLabel("Physical attributes", { exact: true }).fill("80");
  await page
    .getByRole("button", { name: "Save Max Holloway comparison" })
    .click();
  await expect(
    page.getByRole("button", { name: "Load weights" }),
  ).toBeVisible();
  await page.getByRole("textbox", { name: "Search fighters" }).fill("Adesanya");
  await expect(page.locator(".search-results")).toContainText(
    "Israel Adesanya",
  );
  await navigate(page, "Training");
  await page.getByRole("button", { name: "View session" }).first().click();
  await page.getByLabel("Actual minutes").fill("35");
  await page.getByRole("button", { name: "Save workout" }).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Logged" })).toBeVisible();
  await page.getByRole("button", { name: "Logged" }).click();
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("dialog").locator("summary").first(),
  ).toBeFocused();
  await page.keyboard.press("Escape");
  await navigate(page, "Nutrition");
  await expect(
    page.getByRole("heading", { name: "Your seven-day meal template" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Day 7", exact: true }).click();
  await page.getByRole("button", { name: "Grocery list", exact: true }).click();
  await expect(
    page.getByRole("columnheader", { name: "Ingredient" }),
  ).toBeVisible();
  await navigate(page, "Progress");
  await page.getByRole("button", { name: "Weekly check-in" }).click();
  await page.getByLabel("Weight (kg)", { exact: true }).fill("79.2");
  await page.getByLabel("Fatigue (1–10)", { exact: true }).fill("8");
  await page.getByRole("button", { name: "Save check-in" }).click();
  await page.getByRole("button", { name: "Run reassessment" }).click();
  await expect(
    page
      .locator(".card")
      .filter({
        has: page.getByRole("heading", {
          name: "Reassess your development",
          exact: true,
        }),
      })
      .getByText("Recovery flags support reducing workload.", { exact: true }),
  ).toBeVisible();
  await navigate(page, "AI coach");
  await page
    .getByRole("button", { name: "Why did you recommend wrestling?" })
    .click();
  await expect(page.locator(".coach-bubble")).toContainText(
    "Wrestling is priority",
  );
  await expect(page.locator(".coach-bubble")).toContainText(
    "recorded preference/access allocation",
  );
  await expect(page.getByLabel(/Use OpenAI/)).toBeDisabled();
  await page.getByLabel("Available days per week", { exact: true }).fill("3");
  await page.getByRole("button", { name: "Preview change" }).click();
  await page.getByRole("button", { name: "Reject", exact: true }).click();
  await expect(page.getByText("rejected", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Preview change" }).click();
  await page.getByRole("button", { name: "Approve & apply" }).click();
  await expect(page.getByText("approved", { exact: true })).toBeVisible();
  await navigate(page, "Settings & data");
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download all data" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toBe("mma-athlete-report.json");
  expect(await download.failure()).toBeNull();
  const exported = JSON.parse(await readFile((await download.path())!, "utf8"));
  expect(
    exported.records.some(
      (r: { data: { name?: string } }) => r.data.name === "Jordan QA",
    ),
  ).toBeTruthy();
  expect(
    exported.records.filter((r: { kind: string }) => r.kind === "plan"),
  ).toHaveLength(2);
  await noOverflow(page);
});

test("configured AI interface renders labeled interpretation (mocked transport)", async ({
  page,
}) => {
  await seedDemo(page);
  await page.route("**/api/health", (r) =>
    r.fulfill({ json: { status: "ok", ai_configured: true } }),
  );
  await page.route("**/api/coach", async (route) => {
    if (route.request().method() === "POST")
      await route.fulfill({
        json: {
          id: "mock",
          version: 1,
          created_at: new Date().toISOString(),
          data: {
            question: "Explain recovery",
            answer: "Use consistent sleep and reassess workload.",
            mode: "AI-generated interpretation",
            limitations: "Mocked provider for browser QA.",
          },
        },
      });
    else
      await route.fulfill({
        json: [
          {
            id: "mock",
            version: 1,
            created_at: new Date().toISOString(),
            data: {
              question: "Explain recovery",
              answer: "Use consistent sleep and reassess workload.",
              mode: "AI-generated interpretation",
              limitations: "Mocked provider for browser QA.",
            },
          },
        ],
      });
  });
  await navigate(page, "AI coach");
  await page.getByLabel(/Use OpenAI/).check();
  await page.getByLabel("Message your MMA coach").fill("Explain recovery");
  const request = page.waitForRequest(
    (r) => r.url().endsWith("/api/coach") && r.method() === "POST",
  );
  await page.getByRole("button", { name: "Send coaching question" }).click();
  expect((await request).postDataJSON()).toEqual({
    message: "Explain recovery",
    use_ai: true,
  });
  await expect(page.locator(".coach-bubble")).toContainText(
    "AI-generated interpretation",
  );
  await expect(page.locator(".coach-bubble")).toContainText("Mocked provider");
});
