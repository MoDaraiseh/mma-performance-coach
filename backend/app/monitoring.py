"""Fixed-label local alert evaluation; no network, personal-data labels or notifications."""

import argparse
import json
from pathlib import Path


def evaluate_alerts(current, previous=None):
    signals = []

    def signal(code, message, severity="warning"):
        signals.append({"code": code, "severity": severity, "message": message})

    if (
        not isinstance(current, dict)
        or not isinstance(current.get("database"), dict)
        or type(current["database"].get("ready")) is not bool
        or not isinstance(current.get("counters", {}), dict)
        or any(type(v) is not int or v < 0 for v in current.get("counters", {}).values())
    ):
        signal("invalid_snapshot", "Monitoring snapshot is incomplete or malformed.")
        return signals
    if not current["database"]["ready"]:
        signal("database_not_ready", "Database or migration readiness failed.", "critical")
    counters = current.get("counters", {})
    if isinstance(previous, dict) and isinstance(previous.get("counters"), dict):
        before = previous["counters"]
        if all(type(v) is int and v >= 0 for v in before.values()):
            total = counters.get("http.total", 0) - before.get("http.total", 0)
            errors = sum(
                max(0, counters.get("http." + str(n), 0) - before.get("http." + str(n), 0))
                for n in range(500, 600)
            )
            if total >= 20 and errors / total >= 0.05:
                signal("http_error_rate", "At least 5% server errors in a >=20 response sample.")
            if (
                total >= 0
                and counters.get("auth.oidc_failure", 0) - before.get("auth.oidc_failure", 0) >= 5
            ):
                signal(
                    "authentication_failures",
                    "At least five failed managed sign-ins since the prior snapshot.",
                )
    ai = current.get("ai", {})
    if isinstance(ai, dict):
        reservations = ai.get("reserved_outbound_attempts", {})
        if isinstance(reservations, dict):
            for prefix, field in (
                ("day:", "daily_outbound_ceiling"),
                ("month:", "monthly_outbound_ceiling"),
            ):
                limit = ai.get(field)
                if type(limit) is not int or limit <= 0:
                    continue
                if any(
                    isinstance(k, str)
                    and k.startswith(prefix)
                    and type(v) is int
                    and v >= 0.8 * limit
                    for k, v in reservations.items()
                ):
                    signal(
                        "ai_" + field,
                        "AI attempt reservations reached at least 80% of the configured ceiling.",
                    )
    return signals


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    args = parser.parse_args()
    current = json.loads(args.current.read_text(encoding="utf-8"))
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
    print(
        json.dumps(
            {"signals": evaluate_alerts(current, previous), "external_notifications": False},
            indent=2,
        )
    )
