import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("comparison failures clear stale results and manual selection can retry", async ({
  page,
}) => {
  await seedDemo(page);
  await navigate(page, "Comparison lab");
  await expect(page.locator(".match-select")).toHaveCount(3);
  await page.route("**/api/fighter-matches", (route) =>
    route.fulfill({ status: 503, json: { error: "QA matching unavailable" } }),
  );
  await page.getByLabel("Physical attributes", { exact: true }).fill("75");
  await expect(page.getByRole("alert")).toContainText(
    "QA matching unavailable",
  );
  await expect(page.locator(".match-select")).toHaveCount(0);
  await page.unroute("**/api/fighter-matches");
  await page
    .getByRole("button", { name: "Reset weights", exact: true })
    .click();
  await expect(page.locator(".match-select")).toHaveCount(3);
  await page.route("**/api/fighter-comparisons/aspinall", (route) =>
    route.fulfill({ status: 503, json: { error: "QA manual unavailable" } }),
  );
  await page.getByLabel("Search fighters", { exact: true }).fill("Aspinall");
  const select = page
    .locator(".search-results")
    .getByRole("button", { name: "Tom Aspinall" });
  await select.click();
  await expect(page.getByRole("alert")).toContainText("QA manual unavailable");
  await expect(
    page.getByRole("heading", { name: /heuristic resemblance.*coverage/ }),
  ).toHaveCount(0);
  await page.unroute("**/api/fighter-comparisons/aspinall");
  await select.click();
  await expect(
    page.getByRole("heading", { name: /heuristic resemblance.*coverage/ }),
  ).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("comparison controls, manual selection, provenance, favorites and refresh", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Comparison lab");
  await expect(page.locator(".match-select")).toHaveCount(3);
  await page
    .getByText("Physical factors and eligibility filters", { exact: true })
    .click();
  await page.getByLabel("Height factor", { exact: true }).fill("100");
  await page.getByLabel("Reach factor", { exact: true }).fill("0");
  await expect(
    page.getByText("Updating comparisons...", { exact: true }),
  ).toHaveCount(0);
  const heightOrder = await page.locator(".match-select h3").allTextContents();
  await page.getByLabel("Height factor", { exact: true }).fill("0");
  await page.getByLabel("Reach factor", { exact: true }).fill("100");
  await expect
    .poll(async () =>
      (await page.locator(".match-select h3").allTextContents()).join(","),
    )
    .not.toBe(heightOrder.join(","));
  await page
    .getByRole("button", { name: "Reset weights", exact: true })
    .click();
  await page.getByLabel("Search fighters", { exact: true }).fill("Aspinall");
  await page
    .locator(".search-results")
    .getByRole("button", { name: "Tom Aspinall" })
    .click();
  await expect(
    page.getByRole("heading", { name: "You × Tom Aspinall" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: /heuristic resemblance.*coverage/ }),
  ).toBeVisible();
  await expect(
    page.getByText("Current profile division: Heavyweight", { exact: true }),
  ).toBeVisible();
  await page
    .getByText("Sources, division history and data quality", { exact: true })
    .click();
  await expect(
    page.getByRole("table", { name: "Field-level source references" }),
  ).toBeVisible();
  await expect(
    page.getByText(/direct profile access returned 403/),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Save selected comparison", exact: true })
    .click();
  const originalProfile = await (await page.request.get("/api/profile")).json();
  expect(
    (
      await page.request.put("/api/profile", {
        data: { ...originalProfile, height_cm: originalProfile.height_cm + 10 },
      })
    ).ok(),
  ).toBeTruthy();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Comparison lab");
  await page.getByRole("button", { name: "Load weights", exact: true }).click();
  await expect(
    page.getByText(/Charts use the saved athlete profile/),
  ).toBeVisible();
  await expect(
    page
      .getByRole("row", { name: /^Height / })
      .getByRole("cell")
      .nth(1),
  ).toHaveText(`${originalProfile.height_cm} cm`);
  await page
    .getByRole("button", { name: "Re-evaluate with current data", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: /heuristic resemblance.*coverage/ }),
  ).toBeVisible();
  await expect(
    page
      .getByRole("row", { name: /^Height / })
      .getByRole("cell")
      .nth(1),
  ).toHaveText(`${originalProfile.height_cm + 10} cm`);
  await page
    .getByText("Physical factors and eligibility filters", { exact: true })
    .click();
  await page.getByLabel("Division context").selectOption("current");
  await page.getByLabel("Search fighters", { exact: true }).fill("St-Pierre");
  await page
    .locator(".search-results")
    .getByRole("button", { name: "Georges St-Pierre" })
    .click();
  await expect(
    page.getByText(/No compatible active division reference/),
  ).toBeVisible();
  await page.getByLabel("Search fighters", { exact: true }).fill("Nunes");
  await page
    .locator(".search-results")
    .getByRole("button", { name: "Amanda Nunes" })
    .click();
  await expect(
    page.getByRole("heading", { name: /Unscored comparison/ }),
  ).toBeVisible();
  await expect(
    page.getByText(/Different men's\/women's competition category/),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Save selected comparison", exact: true })
    .click();
  await expect(
    page.locator(".card").filter({
      has: page.getByRole("heading", {
        name: "Saved comparisons",
        exact: true,
      }),
    }),
  ).toContainText("Unscored");
  await page
    .getByRole("button", { name: "Refresh reviewed fighter data", exact: true })
    .click();
  await expect(
    page.getByText(/Verification dates have not been advanced/),
  ).toBeVisible();
  await expect(page.locator(".match-select")).toHaveCount(3);
  await page.getByLabel("Search fighters", { exact: true }).fill("");
  await page.locator(".match-select").first().click();
  await expect(
    page.getByRole("heading", { name: /heuristic resemblance.*coverage/ }),
  ).toBeVisible();
  const provenance = page.getByText(
    "Sources, division history and data quality",
    { exact: true },
  );
  if (
    !(await page
      .getByRole("table", { name: "Field-level source references" })
      .isVisible())
  )
    await provenance.click();
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase4-comparison-lab");
  await page.getByLabel("Physical attributes", { exact: true }).focus();
  const before = Number(
    await page.getByLabel("Physical attributes", { exact: true }).inputValue(),
  );
  await page.keyboard.press("ArrowRight");
  await expect(
    page.getByLabel("Physical attributes", { exact: true }),
  ).toHaveValue(String(before + 1));
  for (const label of [
    "Physical attributes",
    "Martial arts background",
    "Fighting style",
    "Stance",
    "Division reference",
  ]) {
    const input = page.getByLabel(label, { exact: true });
    await input.fill("0");
  }
  await expect(
    page.getByText("At least one weight must be positive.", { exact: true }),
  ).toBeVisible();
  await expect(page.locator(".match-select")).toHaveCount(0);
});
