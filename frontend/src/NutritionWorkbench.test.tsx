// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import NutritionWorkbench from "./components/NutritionWorkbench";
import type { NutritionPreferences } from "./types";

const { request } = vi.hoisted(() => ({ request: vi.fn() }));
vi.mock("./api", () => ({ api: request }));
afterEach(cleanup);

it("preserves edited exclusions when an earlier background refresh finishes", async () => {
  const defaults: NutritionPreferences = {
    objective: "Maintain",
    culture: "Varied",
    budget: null,
    dislikes: [],
    unavailable: [],
    add_diet: [],
    add_allergies: [],
    snacks: true,
    hunger: null,
    satisfaction: null,
    training_days: null,
  };
  let pending: Promise<NutritionPreferences> | undefined;
  request.mockImplementation(
    async (path: string, method?: string, body?: unknown) => {
      if (method === "PUT") return { data: body };
      if (path.endsWith("/preferences")) return pending ?? defaults;
      if (path.endsWith("/catalog"))
        return {
          items: [
            {
              id: "tofu",
              name: "Tofu",
              per_100g: {},
              allergens: [],
              source: {},
            },
            {
              id: "rice",
              name: "Rice",
              per_100g: {},
              allergens: [],
              source: {},
            },
          ],
        };
      return [];
    },
  );
  const props = {
    run: async (task: () => Promise<void>) => task(),
    refresh: async () => {},
    busy: false,
  };
  const view = render(<NutritionWorkbench {...props} refreshKey={0} />);
  await screen.findByLabelText("Food dislikes");
  let finish!: (value: NutritionPreferences) => void;
  pending = new Promise((resolve) => {
    finish = resolve;
  });
  view.rerender(<NutritionWorkbench {...props} refreshKey={1} />);
  fireEvent.change(screen.getByLabelText("Food dislikes"), {
    target: { value: "tofu" },
  });
  fireEvent.change(screen.getByLabelText("Unavailable ingredients"), {
    target: { value: "rice" },
  });
  await act(async () => {
    finish(defaults);
    await pending;
  });
  expect(screen.getByLabelText("Food dislikes")).toHaveValue(["tofu"]);
  expect(screen.getByLabelText("Unavailable ingredients")).toHaveValue([
    "rice",
  ]);
  fireEvent.submit(screen.getByLabelText("Food dislikes").closest("form")!);
  await waitFor(() =>
    expect(request).toHaveBeenCalledWith(
      "/nutrition/preferences",
      "PUT",
      expect.objectContaining({ dislikes: ["tofu"], unavailable: ["rice"] }),
    ),
  );
});
