import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  timeout: 30000,
  use: {
    baseURL: "http://localhost:5173",
    viewport: { width: 1440, height: 900 },
    channel: process.env.CHROME_PATH ? undefined : "chrome",
    launchOptions: {
      executablePath: process.env.CHROME_PATH,
    },
  },
  reporter: "list",
});
