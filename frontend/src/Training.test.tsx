// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import Training from "./components/Training";
import { defaultProfile, type Plan, type Saved, type Workout } from "./types";

vi.mock("./api", () => ({ api: async () => [] }));
vi.mock("./components/TrainingInsights", () => ({ default: () => null }));
afterEach(cleanup);

it("blocks opening a session during refresh and closes the old prescription on plan replacement", async () => {
  const plan: Saved<Plan> = {
    id: "first",
    version: 1,
    created_at: "2026-10-31",
    data: {
      version: 1,
      days: 1,
      requested_days: 1,
      inputs: defaultProfile,
      method: "Practice",
      limitations: "Educational",
      weeks: [
        {
          week: 1,
          phase: "Foundation",
          deload: false,
          focus: "Practice",
          sessions: [
            {
              id: "session",
              day: "Monday",
              type: "Strength",
              minutes: 30,
              effort: 5,
              warmup: "Warm up",
              cooldown: "Cool down",
              time_note: "Approximate",
              exercises: [
                {
                  name: "Goblet squat",
                  sets: 1,
                  reps: "6",
                  rest: "60 seconds",
                  cue: "Comfortable motion",
                  substitution: "",
                },
              ],
            },
          ],
        },
      ],
    },
  };
  const props = {
    plan,
    logs: [],
    run: async (task: () => Promise<void>) => task(),
    refresh: async () => {},
  };
  const view = render(<Training {...props} busy />);
  expect(screen.getByRole("button", { name: "View session" })).toBeDisabled();
  view.rerender(<Training {...props} busy={false} />);
  fireEvent.click(screen.getByRole("button", { name: "View session" }));
  expect(screen.getByRole("dialog")).toBeVisible();
  await act(async () =>
    view.rerender(
      <Training
        {...props}
        plan={{ ...plan, id: "second", version: 2 }}
        busy={false}
      />,
    ),
  );
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
});

it("shows a missed log recorded against an earlier version of the same program", () => {
  const session = {
    id: "w2-Monday",
    day: "Monday",
    type: "Strength",
    minutes: 30,
    effort: 5,
    warmup: "Warm up",
    cooldown: "Cool down",
    time_note: "Approximate",
    exercises: [
      {
        name: "Goblet squat",
        sets: 1,
        reps: "6",
        rest: "60 seconds",
        cue: "Comfortable motion",
        substitution: "",
      },
    ],
  };
  const plan: Saved<Plan> = {
    id: "revised",
    version: 2,
    created_at: "2026-11-01",
    data: {
      version: 2,
      days: 1,
      requested_days: 1,
      inputs: defaultProfile,
      method: "Practice",
      limitations: "Educational",
      history_plan_ids: ["original"],
      weeks: [
        {
          week: 1,
          phase: "Foundation",
          deload: false,
          focus: "Practice",
          sessions: [session],
        },
      ],
    },
  };
  const missed: Saved<Workout> = {
    id: "log",
    version: 1,
    created_at: "2026-10-30",
    data: {
      session_id: "w2-Monday",
      plan_id: "original",
      minutes: 0,
      effort: null,
      notes: "",
      status: "missed",
    },
  };
  render(
    <Training
      plan={plan}
      logs={[missed]}
      busy={false}
      run={async (task) => task()}
      refresh={async () => {}}
    />,
  );
  expect(screen.getByRole("button", { name: "Missed" })).toBeInTheDocument();
});
