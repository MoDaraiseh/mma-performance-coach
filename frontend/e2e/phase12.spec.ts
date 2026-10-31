import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("review status is honest and rapid-cut profiles receive no numerical meal plan", async ({
  page,
}, info) => {
  await seedDemo(page);
  await expect(
    page.getByText(/Independent professional review is pending; automated/),
  ).toBeVisible();
  await noOverflow(page);
  const profile = await (await page.request.get("/api/profile")).json();
  expect(
    (
      await page.request.put("/api/profile", {
        data: { ...profile, goal: "Lose 10 kg in 3 days" },
      })
    ).ok(),
  ).toBeTruthy();
  const generated = await (await page.request.post("/api/nutrition")).json();
  expect(generated.data.available).toBe(false);
  expect(generated.data.days).toEqual([]);
  expect(generated.data.target_calories).toBeUndefined();
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Nutrition");
  await expect(page.locator("main")).toContainText(
    "Automated numerical nutrition withheld for a rapid-cutting or extreme-restriction request.",
  );
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase12-withheld-nutrition");
});
