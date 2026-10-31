export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    method,
    credentials: "same-origin",
    headers: body === undefined ? {} : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  }).catch(() => {
    throw new ApiError(
      "Cannot reach the local service. Check that the backend is running, then retry.",
      0,
    );
  });
  const data = await response.json().catch(() => {
    throw new ApiError(
      "The service returned an unreadable response. Please retry.",
      response.status,
    );
  });
  if (!response.ok)
    throw new ApiError(
      data.details
        ? `${data.error}: ${data.details.map((d: { field: string; message: string }) => `${d.field} ${d.message}`).join("; ")}`
        : data.error || "Request failed",
      response.status,
    );
  return data as T;
}
