import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { navigate, noOverflow, evidence } from "./helpers";
import { seedDemo } from "./helpers";

test("active sessions are visible, revocable and preserve recovery access", async ({
  page,
}, info) => {
  const registration = await (
    await page.request.post("/api/auth/register")
  ).json();
  await page.request.post("/api/demo");
  const old = (await page.context().cookies()).find(
    (c) => c.name === "mma_session",
  )!.value;
  expect(
    (
      await page.request.post("/api/auth/restore", {
        data: { token: registration.recovery_token },
      })
    ).ok(),
  ).toBeTruthy();
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Let's get better/ }),
  ).toBeVisible();
  await navigate(page, "Settings & data");
  await expect(
    page.getByRole("heading", { name: "Sign-in and active sessions" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Revoke session created/ }),
  ).toHaveCount(1);
  await page
    .getByRole("button", { name: "Revoke all other sessions", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: /Revoke session created/ }),
  ).toHaveCount(0);
  expect(
    (
      await page.request.get("/api/auth/session", {
        headers: { Cookie: `mma_session=${old}` },
      })
    ).status(),
  ).toBe(401);
  expect((await page.request.get("/api/auth/session")).status()).toBe(200);
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase13-sessions");
  await page
    .getByRole("button", { name: "Revoke session (current)", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: /Train with purpose/ }),
  ).toBeVisible();
  expect(
    (
      await page.request.post("/api/auth/restore", {
        data: { token: registration.recovery_token },
      })
    ).ok(),
  ).toBeTruthy();
  expect((await page.request.get("/api/profile")).status()).toBe(200);
});

test("explicit managed-link control navigates using the validated initiation response (mocked provider UI)", async ({
  page,
}) => {
  await seedDemo(page);
  await page.route("**/api/auth/config", (route) =>
    route.fulfill({
      json: {
        managed_sign_in: true,
        local_registration: false,
        legacy_recovery: true,
      },
    }),
  );
  await page.route("**/api/auth/oidc/link", (route) =>
    route.fulfill({ json: { authorization_url: "/qa-mock-identity" } }),
  );
  await page.route("**/qa-mock-identity", (route) =>
    route.fulfill({
      contentType: "text/html",
      body: "<main><h1>Mock identity provider</h1><p>Browser navigation only; no real identity account or sign-in.</p></main>",
    }),
  );
  await navigate(page, "Settings & data");
  await page
    .getByRole("button", {
      name: "Link managed sign-in to this account",
      exact: true,
    })
    .click();
  await expect(
    page.getByRole("heading", { name: "Mock identity provider" }),
  ).toBeVisible();
});

test("configured managed sign-in explains local-profile migration (mocked provider UI)", async ({
  page,
}) => {
  await page.route("**/api/auth/config", (route) =>
    route.fulfill({
      json: {
        managed_sign_in: true,
        local_registration: false,
        legacy_recovery: true,
      },
    }),
  );
  await page.route("**/api/auth/oidc/login", (route) =>
    route.fulfill({
      contentType: "text/html",
      body: "<main><h1>Mock managed sign-in</h1></main>",
    }),
  );
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Sign in securely" }),
  ).toBeVisible();
  await expect(
    page.getByText(/Existing local profile\? Restore its recovery token/),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Explore the demo" }),
  ).toHaveCount(0);
  await noOverflow(page);
  await page.getByRole("button", { name: "Sign in securely" }).click();
  await expect(
    page.getByRole("heading", { name: "Mock managed sign-in" }),
  ).toBeVisible();
});
