import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { navigate, noOverflow, evidence } from "../e2e/helpers";

test.afterEach(async ({ page }) => {
  if ((await page.request.get("/api/auth/session")).ok()) {
    expect((await page.request.delete("/api/account")).ok()).toBeTruthy();
  }
});

test("complete athlete journey through onboarding, logging, reassessment, approvals and export", async ({
  page,
}, info) => {
  const browserErrors: string[] = [];
  page.on("pageerror", (error) => browserErrors.push(error.message));
  const athleteName = `PG22 ${info.project.name} ${Date.now()}`;
  const docker = path.join(
    process.env.LOCALAPPDATA!,
    "Programs/DockerDesktop/resources/bin/docker.exe",
  );
  expect(["http://127.0.0.1:18018", "http://127.0.0.1:18026"]).toContain(
    info.project.use.baseURL,
  );
  const databaseContainer =
    info.project.use.baseURL === "http://127.0.0.1:18026"
      ? "mma-phase24-patched-database-1"
      : "mma-phase18-isolated-database-1";
  const sql = (query: string) =>
    execFileSync(
      docker,
      [
        "exec",
        databaseContainer,
        "psql",
        "-U",
        "mma_stage_admin",
        "-d",
        "mma_test_stage",
        "-Atc",
        query,
      ],
      { encoding: "utf8" },
    ).trim();
  expect(sql("select version_num from alembic_version")).toBe("0008");
  await page.goto("/");
  await page.getByRole("button", { name: "Build my athlete profile" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await page.getByLabel("Name", { exact: true }).fill(athleteName);
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
    page.getByRole("heading", { name: /PG22/, level: 1 }),
  ).toBeVisible();
  await navigate(page, "Physical analysis");
  await expect(page.locator(".division-big")).toHaveText("Middleweight");
  await navigate(page, "Comparison lab");
  const favorite = page
    .getByRole("button", { name: /^Save .+ comparison$/ })
    .first();
  await expect(favorite).toBeVisible();
  const fighterName = (await favorite.getAttribute("aria-label"))!
    .replace(/^Save /, "")
    .replace(/ comparison$/, "");
  await page.getByLabel("Physical attributes", { exact: true }).fill("80");
  await favorite.click();
  await expect(
    page.getByRole("button", { name: "Load weights" }),
  ).toBeVisible();
  await page
    .getByRole("textbox", { name: "Search fighters" })
    .fill(fighterName);
  await expect(page.locator(".search-results")).toContainText(fighterName);
  await navigate(page, "Training");
  await page.getByRole("button", { name: "View session" }).first().click();
  await page.getByLabel("Actual minutes").fill("35");
  await page
    .getByRole("button", { name: /^Add actual set/ })
    .first()
    .click();
  await page
    .getByLabel(/^Repetitions/)
    .first()
    .fill("8");
  await page
    .getByLabel(/^Load \(kg\)/)
    .first()
    .fill("12");
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
  const nutritionBefore = await (
    await page.request.get("/api/nutrition")
  ).json();
  await page
    .getByRole("button", { name: "Preview lunch substitute", exact: true })
    .click();
  expect((await (await page.request.get("/api/nutrition")).json()).id).toBe(
    nutritionBefore.id,
  );
  await page
    .getByRole("button", { name: "Approve meal plan", exact: true })
    .click();
  await expect(
    page.getByText("Meal plan approved and saved as a new version.", {
      exact: true,
    }),
  ).toBeVisible();
  expect(
    (await (await page.request.get("/api/nutrition")).json()).version,
  ).toBe(nutritionBefore.version + 1);
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
      (r: { data: { name?: string } }) => r.data.name === athleteName,
    ),
  ).toBeTruthy();
  expect(
    exported.records.filter((r: { kind: string }) => r.kind === "plan"),
  ).toHaveLength(2);
  await noOverflow(page);
  expect(
    sql(
      `select count(*) from records where kind='profile' and payload->>'name'='${athleteName}'`,
    ),
  ).toBe("1");
  expect(
    sql(
      `select count(*) from records where kind='workout' and json_array_length(payload->'performances')>0 and user_id=(select user_id from records where kind='profile' and payload->>'name'='${athleteName}')`,
    ),
  ).toBe("1");
  expect(browserErrors).toEqual([]);
  await info.attach("postgres-persistence", {
    body: JSON.stringify({
      database: "mma_test_stage",
      migration: "0008",
      profile_row_found: true,
      workout_performance_row_found: true,
      source: "direct PostgreSQL query",
    }),
    contentType: "application/json",
  });
  await evidence(page, info, "postgres-acceptance");
  page.once("dialog", (dialog) => dialog.accept());
  await page
    .getByRole("button", { name: "Delete my account and data", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Build my athlete profile" }),
  ).toBeVisible();
  expect((await page.request.get("/api/profile")).status()).toBe(401);
  expect(
    sql(
      `select count(*) from records where kind='profile' and payload->>'name'='${athleteName}'`,
    ),
  ).toBe("0");
});
