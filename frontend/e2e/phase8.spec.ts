import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

test("paginated fighter library, source-aware filters and licensed manual comparison", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Comparison lab");
  await expect(
    page.getByText("19 records found; page 1", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Next fighter page" }).click();
  await expect(
    page.getByText("19 records found; page 2", { exact: true }),
  ).toBeVisible();
  await page
    .getByLabel("Search competition category", { exact: true })
    .selectOption("Men");
  await page
    .getByLabel("Search historical division", { exact: true })
    .selectOption("Welterweight");
  await page
    .getByLabel("Search stance", { exact: true })
    .selectOption("Orthodox");
  await page.getByLabel("Search fighters", { exact: true }).fill("Usman");
  await page
    .locator(".search-results")
    .getByRole("button", { name: "Kamaru Usman" })
    .click();
  await expect(
    page.getByRole("heading", { name: /^You .* Kamaru Usman$/ }),
  ).toBeVisible();
  await page
    .getByText("Sources, division history and data quality", { exact: true })
    .click();
  await expect(
    page.getByRole("link", { name: "CC-BY-SA-4.0", exact: true }),
  ).toHaveAttribute("href", "https://creativecommons.org/licenses/by-sa/4.0/");
  await expect(
    page.getByText(/Professional record: Not verified in this snapshot/),
  ).toBeVisible();
  await page
    .getByText("Coverage and data quality report", { exact: true })
    .click();
  await expect(page.getByText(/Men: 11; Women: 8/)).toBeVisible();
  await noOverflow(page);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await evidence(page, info, "phase8-provenance");
});

test("women historical records retain unknown current status and distinguish listed weight", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Comparison lab");
  await page
    .getByLabel("Search competition category", { exact: true })
    .selectOption("Women");
  await page
    .getByLabel("Search career status", { exact: true })
    .selectOption("Unknown");
  await page.getByLabel("Search fighters", { exact: true }).fill("Rousey");
  await page
    .locator(".search-results")
    .getByRole("button", { name: "Ronda Rousey" })
    .click();
  await expect(
    page.getByRole("heading", { name: /^You .* Ronda Rousey$/ }),
  ).toBeVisible();
  await page
    .getByText("Sources, division history and data quality", { exact: true })
    .click();
  await expect(
    page.getByText(
      /Current career status\/division and live record deliberately unknown/,
    ),
  ).toBeVisible();
  const data = await (
    await page.request.get("/api/fighters/search?category=Women&status=Unknown")
  ).json();
  expect(data.total).toBe(4);
  expect(
    data.items.find((f: { id: string }) => f.id === "rousey"),
  ).toMatchObject({ current_division: null, career_status: "Unknown" });
  await noOverflow(page);
  await evidence(page, info, "phase8-women");
});
