import { expect, test } from "@playwright/test";
import { evidence, navigate, noOverflow, seedDemo } from "./helpers";

test("expired session returns to recovery without retaining athlete panels", async ({
  page,
}) => {
  await seedDemo(page);
  await navigate(page, "Settings & data");
  expect((await page.request.delete("/api/account")).status()).toBe(200);
  await page.getByRole("button", { name: "Download all data" }).click();
  await expect(
    page.getByRole("button", { name: "Explore the demo" }),
  ).toBeVisible();
  await expect(
    page.getByText("Returning athlete? Restore with your private token"),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Delete my account and data" }),
  ).toHaveCount(0);
});

test("export, canceled deletion, account deletion and invalidated session", async ({
  page,
}, info) => {
  await seedDemo(page);
  await navigate(page, "Settings & data");
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download all data" }).click();
  expect((await download).suggestedFilename()).toMatch(/json$/);
  await noOverflow(page);
  await evidence(page, info, "phase6-settings");
  page.once("dialog", (dialog) => dialog.dismiss());
  await page
    .getByRole("button", { name: "Delete my account and data" })
    .click();
  expect((await page.request.get("/api/auth/session")).status()).toBe(200);
  page.once("dialog", (dialog) => dialog.accept());
  await page
    .getByRole("button", { name: "Delete my account and data" })
    .click();
  await expect
    .poll(async () => (await page.request.get("/api/auth/session")).status())
    .toBe(401);
  await expect(
    page.getByRole("button", { name: "Explore the demo" }),
  ).toBeVisible();
  expect((await page.request.get("/api/export")).status()).toBe(401);
});
