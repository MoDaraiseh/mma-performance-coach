import { expect, test, type APIRequestContext } from "@playwright/test";

async function register(context: APIRequestContext) {
  let response = await context.post("/api/auth/register");
  if (response.status() === 429) {
    const seconds = Number(response.headers()["retry-after"] || "60");
    expect(seconds).toBeGreaterThanOrEqual(1);
    expect(seconds).toBeLessThanOrEqual(60);
    await new Promise((resolve) => setTimeout(resolve, seconds * 1000));
    response = await context.post("/api/auth/register");
  }
  expect(
    response.status(),
    "Synthetic registration after at most one rate-limit wait",
  ).toBe(200);
}

test("real staging sessions, ownership, host and origin protections", async ({
  page,
  playwright,
  baseURL,
}) => {
  test.setTimeout(150_000);
  const other = await playwright.request.newContext({ baseURL });
  try {
    expect((await page.request.get("/api/ready")).status()).toBe(200);
    expect((await page.request.get("/api/health")).ok()).toBeTruthy();
    await register(page.request);
    expect((await page.request.post("/api/demo")).ok()).toBeTruthy();
    const cookie = (await page.context().cookies()).find(
      (c) => c.name === "mma_session",
    )!;
    expect(cookie.httpOnly).toBe(true);
    expect(cookie.sameSite).toBe("Strict");
    expect(cookie.secure).toBe(false); // Explicit loopback HTTP test mode only.
    await register(other);
    expect((await other.get("/api/profile")).status()).toBe(404);
    const plan = await (await page.request.get("/api/training-plans")).json();
    expect(
      (
        await other.post("/api/training-sessions", {
          data: {
            plan_id: plan.id,
            session_id: plan.data.weeks[0].sessions[0].id,
            minutes: 10,
          },
        })
      ).status(),
    ).toBe(404);
    expect(
      (
        await page.request.get("/api/ready", {
          headers: { Host: "unexpected.invalid" },
        })
      ).status(),
    ).toBe(400);
    expect(
      (
        await page.request.post("/api/progress", {
          headers: { Origin: "https://untrusted.invalid" },
          data: {},
        })
      ).status(),
    ).toBe(403);
    const response = await page.request.get("/api/health");
    expect(response.headers()["x-content-type-options"]).toBe("nosniff");
    expect(response.headers()["x-frame-options"]).toBe("DENY");
    expect(response.headers()["content-security-policy"]).toContain(
      "frame-ancestors 'none'",
    );
  } finally {
    await other.delete("/api/account");
    await other.dispose();
    await page.request.delete("/api/account");
  }
});
