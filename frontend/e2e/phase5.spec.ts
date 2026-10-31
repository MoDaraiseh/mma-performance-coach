import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("source-backed nutrition, feedback, meal preview, reject and approval", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Nutrition");
  await expect(
    page.getByRole("heading", { name: "Estimated fueling targets" }),
  ).toBeVisible();
  const original = await (await page.request.get("/api/nutrition")).json();
  await page
    .getByRole("button", { name: "Preview lunch substitute", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Reject meal plan", exact: true }),
  ).toBeVisible();
  expect((await (await page.request.get("/api/nutrition")).json()).id).toBe(
    original.id,
  );
  await page
    .getByRole("button", { name: "Reject meal plan", exact: true })
    .click();
  await page.getByText("Edit nutrition preferences", { exact: true }).click();
  await page
    .getByLabel("Food dislikes", { exact: true })
    .selectOption(["tofu"]);
  await page
    .getByLabel("Unavailable ingredients", { exact: true })
    .selectOption(["rice"]);
  await page
    .getByLabel("Ingredient pattern preference")
    .selectOption("Middle Eastern inspired");
  await page.getByLabel("Food budget preference").selectOption("Low");
  await page
    .getByLabel("Hunger (optional, 1 low–5 high)", { exact: true })
    .fill("3");
  await noOverflow(page);
  await page
    .getByRole("button", { name: "Save nutrition feedback", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Individual guidance is needed" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Preview updated meal plan", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Approve meal plan", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Your seven-day meal template" }),
  ).toBeVisible();
  const current = await (await page.request.get("/api/nutrition")).json();
  expect(current.version).toBe(original.version + 1);
  expect(
    current.data.days.flatMap(
      (d: { meals: { ingredients: { id: string }[] }[] }) =>
        d.meals.flatMap((m) => m.ingredients.map((i) => i.id)),
    ),
  ).not.toEqual(expect.arrayContaining(["rice"]));
  await page
    .getByText("Inspect 40 source-backed ingredients", { exact: true })
    .click();
  const riceSummary = page
    .locator("summary")
    .filter({ hasText: /^rice \(cooked\)$/ });
  await riceSummary.click();
  const rice = riceSummary.locator("..");
  await expect(rice).toContainText("CC0-1.0");
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase5-nutrition");
});

test("local adaptive coach proposes real edits and applies only after approval", async ({
  page,
}, info) => {
  await seedDemo(page);
  const original = await (await page.request.get("/api/training-plans")).json();
  await navigate(page, "AI coach");
  await page
    .getByLabel("Message your MMA coach", { exact: true })
    .fill("Make my Monday workout shorter to 20 minutes");
  await page
    .getByRole("button", { name: "Send coaching question", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Approve coaching change", exact: true }),
  ).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-plans")).json()).id,
  ).toBe(original.id);
  await page
    .getByText("Review before and after workout prescriptions", { exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Proposed: Monday · 20 minutes" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Approve coaching change", exact: true })
    .click();
  await expect(page.getByText("approved", { exact: true })).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-plans")).json()).version,
  ).toBe(original.version + 1);
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase5-coaching");
  await navigate(page, "Nutrition");
  await expect(
    page.getByText(/Approved training volume changed/),
  ).toBeVisible();
});

test("stale nutrition proposal refuses approval after changed feedback", async ({
  page,
}) => {
  await seedDemo(page);
  await navigate(page, "Nutrition");
  await page
    .getByRole("button", { name: "Preview updated meal plan", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Approve meal plan", exact: true }),
  ).toBeVisible();
  const prefs = await (
    await page.request.get("/api/nutrition/preferences")
  ).json();
  expect(
    (
      await page.request.put("/api/nutrition/preferences", {
        data: { ...prefs, add_diet: ["Vegan"] },
      })
    ).ok(),
  ).toBeTruthy();
  await page
    .getByRole("button", { name: "Approve meal plan", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("changed");
  expect(
    (await (await page.request.get("/api/nutrition/history")).json()).length,
  ).toBe(1);
});
