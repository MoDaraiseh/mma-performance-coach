import { defineConfig } from "@playwright/test";

// README screenshots (docs/images/). Same disposable QA server as the browser
// suite: a throwaway database under .qa-runtime/ and no AI key. Run with
// `npm run screenshots`; it is not part of the QA suite.
const python =
  process.platform === "win32"
    ? "../.venv/Scripts/python.exe"
    : "../.venv/bin/python";
export default defineConfig({
  testDir: "./screenshots",
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  expect: { timeout: 10_000 },
  retries: 0,
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:8123",
    channel: process.env.PW_CHANNEL || "msedge",
    headless: true,
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
    colorScheme: "light",
  },
  webServer: {
    command: `"${python}" ../backend/tests/serve_browser_qa.py`,
    url: "http://127.0.0.1:8123/api/health",
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
