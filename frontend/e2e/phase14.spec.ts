import { expect, test } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { navigate, noOverflow, seedDemo } from "./helpers";

test("release load and dashboard timings use actual browser observations", async ({
  page,
}, info) => {
  await seedDemo(page);
  const samples = [];
  for (let i = 0; i < 3; i++) {
    const started = performance.now();
    await page.reload();
    await expect(
      page.getByRole("heading", { name: /Let's get better/ }),
    ).toBeVisible();
    const overviewReadyMs = performance.now() - started;
    const navigation = await page.evaluate(() => {
      const entry = performance.getEntriesByType(
        "navigation",
      )[0] as PerformanceNavigationTiming;
      return {
        domContentLoadedMs: entry.domContentLoadedEventEnd,
        loadMs: entry.loadEventEnd,
        documentTransferBytes: entry.transferSize,
      };
    });
    const dashboardStarted = performance.now();
    const response = page.waitForResponse(
      (r) => r.url().includes("/api/analytics?") && r.status() === 200,
    );
    await navigate(page, "Progress");
    await response;
    await expect(
      page.getByText("Loading athlete analytics…", { exact: true }),
    ).toHaveCount(0);
    await expect(
      page.getByRole("heading", { name: "Athletic development dashboard" }),
    ).toBeVisible();
    await expect(page.getByText(/recorded events analyzed\./)).toBeVisible();
    await noOverflow(page);
    samples.push({
      overviewReadyMs,
      dashboardReadyMs: performance.now() - dashboardStarted,
      ...navigation,
    });
  }
  const directory = path.resolve(
    process.env.PW_EVIDENCE_DIR || "../docs/evidence/phase14",
  );
  await mkdir(directory, { recursive: true });
  await writeFile(
    path.join(directory, `${info.project.name}-load-performance.json`),
    JSON.stringify(
      {
        browser: page.context().browser()?.version(),
        viewport: page.viewportSize(),
        fixture:
          "Synthetic demo, three warm reloads; local HTTP; no throttling",
        limitation: "Includes test polling; not a cold-load or production SLA",
        samples,
      },
      null,
      2,
    ),
  );
});
