import { expect, test } from "@playwright/test";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("expanded sources and fat-food replacements remain explicit and versioned", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Training");
  await expect(
    page.getByRole("heading", { name: "General fitness and MMA development" }),
  ).toBeVisible();
  await page
    .getByLabel("Exercise category", { exact: true })
    .selectOption("Mobility");
  await expect(page.locator(".exercise")).toHaveCount(2);
  await page.getByText(/Supported ankle rocks/).click();
  await expect(
    page.getByText(/Objective: Ankle mobility practice/),
  ).toBeVisible();
  await noOverflow(page);
  await navigate(page, "Comparison lab");
  await page
    .getByRole("textbox", { name: "Search fighters" })
    .fill("Alexander Volkov");
  await expect(page.locator(".search-results")).toContainText(
    "Alexander Volkov",
  );
  await navigate(page, "Nutrition");
  await expect(
    page.getByText("Inspect 55 source-backed ingredients", { exact: true }),
  ).toBeVisible();
  const original = await (await page.request.get("/api/nutrition")).json();
  await page
    .getByLabel("Replacement food", { exact: true })
    .selectOption("almonds");
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
      (i: { id: string }) => i.id === "almonds",
    ),
  ).toBeTruthy();
  const history = await (
    await page.request.get("/api/nutrition/history")
  ).json();
  expect(
    history.find((r: { id: string }) => r.id === original.id).data.days,
  ).toEqual(original.data.days);
  await noOverflow(page);
  await evidence(page, info, "phase15-approved-food-replacement");

  const profile = await (await page.request.get("/api/profile")).json();
  profile.allergies = ["nuts"];
  expect(
    (await page.request.put("/api/profile", { data: profile })).ok(),
  ).toBeTruthy();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Nutrition");
  await page
    .getByRole("button", { name: "Preview updated meal plan", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Approve meal plan", exact: true })
    .click();
  await expect(
    page.getByText("Meal plan approved and saved as a new version.", {
      exact: true,
    }),
  ).toBeVisible();
  const safe = await (await page.request.get("/api/nutrition")).json();
  await page
    .getByLabel("Replacement food", { exact: true })
    .selectOption("peanut-butter");
  await page
    .getByRole("button", {
      name: "Preview chosen food replacement",
      exact: true,
    })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "excluded or unavailable",
  );
  expect((await (await page.request.get("/api/nutrition")).json()).id).toBe(
    safe.id,
  );
  await noOverflow(page);
  await evidence(page, info, "phase15-allergy-rejection");
});
