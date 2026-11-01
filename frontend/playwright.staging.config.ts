import { defineConfig } from "@playwright/test";
import baseline from "./playwright.config";

// Explicit external PostgreSQL staging only: never start the SQLite QA server.
export default defineConfig({
  ...baseline,
  testDir: "./staging-e2e",
  webServer: undefined,
  timeout: 90_000,
  outputDir: "test-results-staging",
  reporter: [
    ["list"],
    [
      "json",
      {
        outputFile:
          process.env.PW_STAGING_REPORT ||
          "../docs/evidence/phase22/browser-results.json",
      },
    ],
  ],
  use: {
    ...baseline.use,
    baseURL: "http://127.0.0.1:18018",
    // These live tests handle synthetic recovery tokens: retain no request traces.
    trace: "off",
  },
});
