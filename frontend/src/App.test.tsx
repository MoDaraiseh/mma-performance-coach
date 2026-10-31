// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";
import Wizard from "./components/Wizard";
import { defaultProfile } from "./types";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it("saves discipline-specific goals, coaching preferences and exact weekdays", async () => {
  const save = vi.fn().mockResolvedValue(undefined);
  render(
    <Wizard
      initial={{
        ...defaultProfile,
        name: "Jordan",
        experience: [
          {
            discipline: "Boxing",
            level: "Beginner",
            months: 3,
            sessions: 1,
            instructor: true,
            competition: false,
            strengths: "",
            weaknesses: "",
            interested: true,
          },
        ],
      }}
      onClose={vi.fn()}
      onSave={save}
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Go to step 3" }));
  fireEvent.change(screen.getByLabelText("Technical goals for Boxing"), {
    target: { value: "Defensive exits" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Go to step 4" }));
  fireEvent.click(
    screen.getByLabelText(
      "Access to a qualified strength and conditioning coach",
    ),
  );
  fireEvent.click(screen.getByRole("button", { name: "Go to step 5" }));
  fireEvent.click(screen.getByLabelText("Tuesday", { exact: true }));
  fireEvent.click(screen.getByLabelText("Thursday", { exact: true }));
  fireEvent.click(screen.getByRole("button", { name: "Go to step 6" }));
  fireEvent.click(screen.getByRole("button", { name: "Save athlete profile" }));
  await waitFor(() =>
    expect(save).toHaveBeenCalledWith(
      expect.objectContaining({
        strength_coach: true,
        available_days: ["Tuesday", "Thursday"],
        experience: [
          expect.objectContaining({ technical_goals: "Defensive exits" }),
        ],
      }),
    ),
  );
});

describe("athlete assessment", () => {
  it("keeps dialog focus inside and supports Escape", () => {
    const close = vi.fn();
    render(
      <Wizard
        initial={{ ...defaultProfile, name: "Sam" }}
        onClose={close}
        onSave={vi.fn()}
      />,
    );
    expect(
      screen.getByRole("button", { name: "Close assessment" }),
    ).toHaveFocus();
    fireEvent.keyDown(document, { key: "Tab", shiftKey: true });
    expect(screen.getByRole("button", { name: "Continue" })).toHaveFocus();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(close).toHaveBeenCalledOnce();
  });
  it("makes background content inert while a modal is open and restores it on close", () => {
    const { unmount } = render(
      <>
        <button>Background action</button>
        <Wizard
          initial={{ ...defaultProfile, name: "Sam" }}
          onClose={vi.fn()}
          onSave={vi.fn()}
        />
      </>,
    );
    const background = screen.getByText("Background action");
    expect(background.inert).toBe(true);
    unmount();
    expect(background.inert).toBe(false);
  });
  it("supports previous answers, optional blank measurements and saves a typed profile", async () => {
    const save = vi.fn().mockResolvedValue(undefined);
    render(
      <Wizard
        initial={{ ...defaultProfile, name: "Test Athlete" }}
        onClose={() => {}}
        onSave={save}
      />,
    );
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Sam Athlete" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Continue" }));
    expect(screen.getByLabelText(/Total wingspan/)).toHaveValue(null);
    fireEvent.change(screen.getByLabelText(/Total wingspan/), {
      target: { value: "186" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Back" }));
    expect(screen.getByLabelText("Name")).toHaveValue("Sam Athlete");
    fireEvent.click(screen.getByRole("button", { name: "Go to step 6" }));
    fireEvent.click(
      screen.getByRole("button", { name: "Save athlete profile" }),
    );
    await waitFor(() =>
      expect(save).toHaveBeenCalledWith(
        expect.objectContaining({
          name: "Sam Athlete",
          wingspan_cm: 186,
          standing_reach_cm: null,
          is_demo: false,
        }),
      ),
    );
  });
  it("saves drafts to the backend and makes save failures visible", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ id: "draft" }) });
    vi.stubGlobal("fetch", fetch);
    render(
      <Wizard
        initial={{ ...defaultProfile, name: "Draft Athlete" }}
        onClose={() => {}}
        onSave={vi.fn().mockRejectedValue(new Error("Profile unavailable"))}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Save progress" }));
    await screen.findByText("Draft saved");
    expect(fetch).toHaveBeenCalledWith(
      "/api/profile/draft",
      expect.objectContaining({ method: "PUT" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Go to step 6" }));
    fireEvent.click(
      screen.getByRole("button", { name: "Save athlete profile" }),
    );
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Profile unavailable",
    );
  });
  it("converts imperial measurements to canonical metric values", () => {
    render(
      <Wizard
        initial={{ ...defaultProfile, name: "Sam" }}
        onClose={() => {}}
        onSave={vi.fn()}
      />,
    );
    fireEvent.change(screen.getByLabelText("Measurement units"), {
      target: { value: "imperial" },
    });
    fireEvent.change(screen.getByLabelText("Height (in)"), {
      target: { value: "72" },
    });
    fireEvent.change(screen.getByLabelText("Measurement units"), {
      target: { value: "metric" },
    });
    expect(screen.getByLabelText("Height (cm)")).toHaveValue(182.88);
  });
});

describe("API error handling", () => {
  it("gives actionable feedback when the backend cannot be reached", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );
    await expect(api("/profile")).rejects.toThrow(
      "Check that the backend is running",
    );
  });
  it("reports unreadable server errors without leaking a JSON parser exception", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        status: 502,
        json: async () => {
          throw new SyntaxError("Unexpected token <");
        },
      }),
    );
    await expect(api("/profile")).rejects.toThrow("unreadable response");
  });
  it("surfaces field validation errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({
          error: "Invalid input",
          details: [{ field: "body.days", message: "must be at most 6" }],
        }),
      }),
    );
    await expect(api("/profile", "PUT", { days: 7 })).rejects.toThrow(
      "body.days must be at most 6",
    );
  });
});
