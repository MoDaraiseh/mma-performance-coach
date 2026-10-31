import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("longitudinal dashboard uses actual measurements and saves technical achievements", async ({
  page,
}, info) => {
  await seedDemo(page);
  const plan = await (await page.request.get("/api/training-plans")).json();
  for (const [days, load] of [
    [28, 40],
    [14, 45],
    [0, 50],
  ]) {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    const response = await page.request.post("/api/progress", {
      data: {
        date: date.toISOString().slice(0, 10),
        weight_kg: 80,
        sleep: 8,
        fatigue: 3,
        benchmarks: [
          {
            name: "Bench press",
            value: load,
            unit: "kg",
            reps: 5,
            effort: 7,
            provenance: "measured",
          },
        ],
      },
    });
    expect(response.ok()).toBeTruthy();
  }
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Progress");
  await expect(
    page.getByRole("heading", { name: "Athletic development dashboard" }),
  ).toBeVisible();
  const selector = page.getByLabel("Development metric", { exact: true });
  await expect(selector.locator("option")).not.toHaveCount(0);
  const value = await selector
    .locator("option")
    .evaluateAll(
      (options) =>
        (
          options.find(
            (o) =>
              o.textContent?.includes("Bench press") &&
              o.textContent?.includes("kg") &&
              !o.textContent?.includes("ratio"),
          ) as HTMLOptionElement
        )?.value,
    );
  expect(value).toBeTruthy();
  await selector.selectOption(value!);
  await expect(page.locator(".athlete-analytics")).toContainText(
    "Window baseline: 40 kg",
  );
  await expect(page.locator(".athlete-analytics")).toContainText(
    "latest: 50 kg",
  );
  await page
    .getByLabel("Technical achievement", { exact: true })
    .fill("Completed coached defensive footwork sequence");
  await page
    .getByRole("button", { name: "Save technical achievement", exact: true })
    .click();
  await expect(
    page.getByText(
      "Technical achievement saved as a self-reported milestone.",
      { exact: true },
    ),
  ).toBeVisible();
  await expect(page.locator(".athlete-analytics")).toContainText(
    "Completed coached defensive footwork sequence",
  );
  expect(
    (await (await page.request.get("/api/training-plans")).json()).id,
  ).toBe(plan.id);
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download progress CSV" }).click();
  expect((await download).suggestedFilename()).toBe("athlete-progress.csv");
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include(".athlete-analytics").analyze())
      .violations,
  ).toEqual([]);
  await evidence(page, info, "phase11-development");
});

test("empty analytics never invents measurements", async ({ page }, info) => {
  await seedDemo(page);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Progress");
  await expect(page.locator(".athlete-analytics")).toContainText(
    "0 of 0 recorded events analyzed",
  );
  await expect(
    page.getByLabel("Development metric", { exact: true }),
  ).toContainText("No measured series");
  await noOverflow(page);
  await evidence(page, info, "phase11-empty");
});

test("history pagination, calendar anchor, report download and date filters", async ({
  page,
}) => {
  await seedDemo(page);
  const plan = await (await page.request.get("/api/training-plans")).json();
  for (let days = 0; days < 12; days++) {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - days);
    expect(
      (
        await page.request.post("/api/progress", {
          data: {
            date: date.toISOString().slice(0, 10),
            weight_kg: 80,
            sleep: 8,
            fatigue: 3,
          },
        })
      ).ok(),
    ).toBeTruthy();
  }
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Progress");
  await expect(page.locator(".athlete-analytics")).toContainText(
    "12 check-ins in this interval; page 1.",
  );
  await page
    .getByRole("button", { name: "Next measurement page", exact: true })
    .click();
  await expect(page.locator(".athlete-analytics")).toContainText(
    "12 check-ins in this interval; page 2.",
  );
  await expect(
    page
      .getByRole("region", { name: "Check-in history", exact: true })
      .locator("tbody tr"),
  ).toHaveCount(2);
  const monday = new Date();
  // Fixture dates are submitted as UTC ISO days; local weekday arithmetic can
  // turn Monday into Sunday before 04:00 on the Dubai test host.
  monday.setUTCDate(monday.getUTCDate() - ((monday.getUTCDay() + 6) % 7) - 14);
  await page
    .getByLabel("Analytics cycle start (Monday)", { exact: true })
    .fill(monday.toISOString().slice(0, 10));
  await page
    .getByRole("button", { name: "Save analytics cycle start", exact: true })
    .click();
  await expect(
    page.getByText(
      "Analytics cycle start saved. Approved workouts were not changed.",
      { exact: true },
    ),
  ).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-plans")).json()).id,
  ).toBe(plan.id);
  const downloading = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download development report", exact: true })
    .click();
  const file = await downloading;
  const report = JSON.parse(await readFile((await file.path())!, "utf8"));
  expect(report.coverage.loaded_events).toBe(12);
  expect(report.adherence.planned).toBeGreaterThan(0);
  await page
    .getByLabel("Analytics start date", { exact: true })
    .fill(new Date().toISOString().slice(0, 10));
  await expect(page.locator(".athlete-analytics")).toContainText(
    "1 of 1 recorded events analyzed",
  );
  await expect(page.locator(".athlete-analytics")).toContainText(
    "1 check-ins in this interval; page 1.",
  );
});
