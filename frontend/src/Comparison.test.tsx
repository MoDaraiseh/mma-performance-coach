// @vitest-environment jsdom
import "@testing-library/jest-dom/vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import Comparison from "./components/Comparison";
import { defaultProfile } from "./types";

const { request } = vi.hoisted(() => ({ request: vi.fn() }));
vi.mock("./api", () => ({ api: request }));
afterEach(cleanup);

it("uses server pagination and resets to the first page when a search filter changes", async () => {
  request.mockImplementation(async (path: string) => {
    if (path.startsWith("/fighters/search?"))
      return { items: [{ id: "qa", name: "Synthetic QA" }], total: 17 };
    if (path === "/fighter-data")
      return {
        count: 17,
        unavailable_records: [],
        providers: [],
        revisions: [],
      };
    if (path === "/fighter-matches")
      return { matches: [], weights: { physical: 100 }, method: "Test" };
    return [];
  });
  render(
    <Comparison
      profile={defaultProfile}
      run={async (task) => task()}
      busy={false}
      notify={vi.fn()}
    />,
  );
  await screen.findByRole("button", { name: "Synthetic QA" });
  fireEvent.click(screen.getByRole("button", { name: "Next fighter page" }));
  await waitFor(() =>
    expect(request).toHaveBeenCalledWith(expect.stringContaining("page=2")),
  );
  fireEvent.change(screen.getByLabelText("Search competition category"), {
    target: { value: "Women" },
  });
  await waitFor(() =>
    expect(request).toHaveBeenCalledWith(
      expect.stringMatching(/page=1.*category=Women/),
    ),
  );
  expect(request).not.toHaveBeenCalledWith("/fighters");
});
