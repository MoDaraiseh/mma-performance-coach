import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("nutrition cooking preferences and chosen food replacement preserve approved history", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Nutrition");
  await page.getByText("Edit nutrition preferences", { exact: true }).click();
  await page
    .getByLabel("Cooking skill", { exact: true })
    .selectOption("Comfortable");
  await page
    .getByLabel("Assembly time limit (minutes)", { exact: true })
    .fill("10");
  await page.getByLabel("Meals per day", { exact: true }).selectOption("3");
  await page
    .getByRole("button", { name: "Save nutrition feedback", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Preview updated meal plan", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Approve meal plan", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Your seven-day meal template" }),
  ).toBeVisible();
  const original = await (await page.request.get("/api/nutrition")).json();
  expect(
    original.data.days.every((d: { meals: unknown[] }) => d.meals.length === 3),
  ).toBeTruthy();
  expect(original.data.preferences.cooking_minutes).toBe(10);
  const replacement = original.data.days[0].meals[1].ingredients.some(
    (i: { id: string }) => i.id === "pasta",
  )
    ? "rice"
    : "pasta";
  await page
    .getByLabel("Replacement food", { exact: true })
    .selectOption(replacement);
  await page
    .getByRole("button", {
      name: "Preview chosen food replacement",
      exact: true,
    })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Substitution differences before approval",
    }),
  ).toBeVisible();
  expect((await (await page.request.get("/api/nutrition")).json()).id).toBe(
    original.id,
  );
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase9-substitution");
  await page
    .getByRole("button", { name: "Approve meal plan", exact: true })
    .click();
  await expect(
    page.getByText("Meal plan approved and saved as a new version.", {
      exact: true,
    }),
  ).toBeVisible();
  const current = await (await page.request.get("/api/nutrition")).json();
  expect(current.version).toBe(original.version + 1);
  expect(
    current.data.days[0].meals[1].ingredients.some(
      (i: { id: string }) => i.id === replacement,
    ),
  ).toBeTruthy();
  const versions = await (
    await page.request.get("/api/nutrition/history")
  ).json();
  expect(
    versions.find((r: { id: string }) => r.id === original.id).data,
  ).toMatchObject({
    preferences: original.data.preferences,
    days: original.data.days,
    grocery: original.data.grocery,
  });
});
