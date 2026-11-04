import { defineConfig } from "@playwright/test";
import staging from "./playwright.staging.config";

// Fixed separate candidate endpoint; never start or mutate the original staging stack.
export default defineConfig({
  ...staging,
  outputDir: "test-results-candidate",
  reporter: [
    ["list"],
    [
      "json",
      {
        outputFile:
          process.env.PW_STAGING_REPORT ||
          "../docs/evidence/phase24/browser-results.json",
      },
    ],
  ],
  use: { ...staging.use, baseURL: "http://127.0.0.1:18026" },
});
