import { expect, test, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { seedDemo, navigate, noOverflow, evidence } from "./helpers";

async function ask(page: Page, text: string) {
  await page.getByLabel("Message your MMA coach", { exact: true }).fill(text);
  await page
    .getByRole("button", { name: "Send coaching question", exact: true })
    .click();
  await expect(page.locator(".user-bubble").last()).toHaveText(text);
  await expect
    .poll(() =>
      page
        .locator(".coach-bubble")
        .last()
        .evaluate((el) => {
          const bubble = el.getBoundingClientRect(),
            chat = el.closest(".chat")!.getBoundingClientRect();
          return bubble.bottom <= chat.bottom + 1 && bubble.bottom >= chat.top;
        }),
    )
    .toBeTruthy();
}

test("coach assessment and reschedule previews persist only after approval", async ({
  page,
}, info) => {
  await seedDemo(page);
  const before = await (await page.request.get("/api/training-plans")).json();
  await navigate(page, "AI coach");
  await ask(page, "Request an updated assessment");
  await expect(
    page.getByRole("heading", { name: "Updated assessment preview" }),
  ).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-plans")).json()).id,
  ).toBe(before.id);
  await page
    .getByRole("button", { name: "Approve coaching change", exact: true })
    .click();
  await expect(page.getByText(/Saved assessment version 1/)).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-plans")).json()).id,
  ).toBe(before.id);
  const source = before.data.weeks[0].sessions.find(
    (s: { exercises: { coached?: boolean }[] }) =>
      s.exercises.every((e) => !e.coached),
  );
  expect(source).toBeTruthy();
  const target = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ].find(
    (d) =>
      !before.data.weeks[0].sessions.some((s: { day: string }) => s.day === d),
  );
  await ask(page, `Reschedule my ${source.day} workout to ${target} in week 1`);
  await expect(
    page.getByRole("button", { name: "Approve coaching change", exact: true }),
  ).toBeVisible();
  await page
    .getByText("Review before and after workout prescriptions", { exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: `Proposed: ${target} · ${source.minutes} minutes`,
    }),
  ).toBeVisible();
  await noOverflow(page);
  expect(
    (await new AxeBuilder({ page }).include("main").analyze()).violations,
  ).toEqual([]);
  await evidence(page, info, "phase10-reschedule");
  await page
    .getByRole("button", { name: "Approve coaching change", exact: true })
    .click();
  await expect(page.getByText(/Saved training version/)).toBeVisible();
  const after = await (await page.request.get("/api/training-plans")).json();
  expect(after.version).toBe(before.version + 1);
  expect(
    after.data.weeks[0].sessions.find((s: { id: string }) => s.id === source.id)
      .day,
  ).toBe(target);
  expect(
    (await (await page.request.get("/api/nutrition")).json()).data.available,
  ).toBeFalsy();
});

test("coach frequency diffs, unsupported progression and context transparency", async ({
  page,
}, info) => {
  await seedDemo(page);
  const before = await (await page.request.get("/api/training-plans")).json();
  await navigate(page, "AI coach");
  await ask(page, "Propose training progression from week 3");
  await expect(
    page.getByText(/No change prepared: No evidence-supported progression/),
  ).toBeVisible();
  await ask(page, "Change training frequency to 3 days per week from week 2");
  await expect(
    page.getByRole("button", { name: "Approve coaching change", exact: true }),
  ).toBeVisible();
  await page
    .getByText("Review weekly schedule differences", { exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Proposed week 2", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Reject coaching change", exact: true })
    .click();
  await expect(page.getByText("rejected", { exact: true })).toBeVisible();
  expect(
    (await (await page.request.get("/api/training-plans")).json()).id,
  ).toBe(before.id);
  await ask(page, "Explain my progress and possible plateaus");
  await expect(
    page.getByText(/No comparable benchmark change is established/).last(),
  ).toBeVisible();
  await page
    .getByText("Context and evidence used", { exact: true })
    .last()
    .click();
  await expect(
    page.getByText(/Athlete inputs are self-reported/).last(),
  ).toBeVisible();
  await noOverflow(page);
  await evidence(page, info, "phase10-context");
});
