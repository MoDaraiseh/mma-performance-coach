import { useEffect, useState } from "react";
import { api } from "../api";
import { Card, Note } from "./ui";
import type { Runner } from "../types";

interface Session {
  id: string;
  label: string;
  created_at: string;
  expires_at: string;
  current: boolean;
}
export default function SessionSecurity({
  run,
  busy,
}: {
  run: Runner;
  busy: boolean;
}) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [managed, setManaged] = useState(false);
  const [error, setError] = useState("");
  const reload = async () =>
    setSessions(await api<Session[]>("/auth/sessions"));
  useEffect(() => {
    Promise.all([
      api<{ managed_sign_in: boolean }>("/auth/config"),
      api<Session[]>("/auth/sessions"),
    ])
      .then(([config, rows]) => {
        setManaged(config.managed_sign_in);
        setSessions(rows);
      })
      .catch(() =>
        setError("Session security could not load. Reload to retry."),
      );
  }, []);
  return (
    <Card title="Sign-in and active sessions">
      <Note>
        Managed identity provides provider-controlled recovery and optional MFA.
        Linking is explicit and preserves your existing local recovery
        credential. Local recovery remains an alternative until the operator
        disables it. Session labels describe sign-in method; physical devices
        are not independently identified. Legacy sessions migrated from older
        releases use migration time when the original creation time is unknown.
      </Note>
      {managed && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            run(async () => {
              const result = await api<{ authorization_url: string }>(
                "/auth/oidc/link",
                "POST",
              );
              window.location.assign(result.authorization_url);
            });
          }}
        >
          <button className="secondary" disabled={busy}>
            Link managed sign-in to this account
          </button>
        </form>
      )}
      {error && <p role="alert">{error}</p>}
      {sessions.map((s) => (
        <div className="settings-row" key={s.id}>
          <div>
            <strong>
              {s.label}
              {s.current ? " (current)" : ""}
            </strong>
            <p>
              Created {new Date(s.created_at).toLocaleString()}; expires{" "}
              {new Date(s.expires_at).toLocaleString()}.
            </p>
          </div>
          <button
            className="secondary"
            disabled={busy}
            aria-label={
              s.current
                ? "Revoke session (current)"
                : `Revoke session created ${s.created_at}`
            }
            onClick={() =>
              run(async () => {
                await api(`/auth/sessions/${s.id}`, "DELETE");
                if (s.current) window.location.reload();
                else await reload();
              })
            }
          >
            Revoke session
          </button>
        </div>
      ))}
      {!sessions.length && !error && (
        <p role="status">Loading active sessions…</p>
      )}
      <button
        className="secondary"
        disabled={busy}
        onClick={() =>
          run(async () => {
            await api("/auth/sessions/revoke-others", "POST");
            await reload();
          })
        }
      >
        Revoke all other sessions
      </button>
    </Card>
  );
}
