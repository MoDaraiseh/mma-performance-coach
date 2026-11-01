"""Fixed-label monitoring with bounded loopback collection; no external notifications."""

import argparse
import json
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


def evaluate_alerts(current, previous=None, trend_previous=None):
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
    application = current.get("application")
    if isinstance(application, dict):
        if application.get("available") is False:
            signal("application_unavailable", "Application liveness check failed.", "critical")
        elif application.get("ready") is False:
            signal("application_not_ready", "Application readiness check failed.", "critical")
    if isinstance(previous, dict):
        if previous.get("database", {}).get("ready") is False and current["database"]["ready"]:
            signal("database_recovered", "Database readiness recovered.", "info")
        old_app = previous.get("application", {})
        if (
            isinstance(application, dict)
            and old_app.get("available") is False
            and application.get("available") is True
        ):
            signal("application_recovered", "Application liveness recovered.", "info")
        if (
            isinstance(application, dict)
            and old_app.get("ready") is False
            and application.get("ready") is True
        ):
            signal("application_readiness_recovered", "Application readiness recovered.", "info")
    metrics_previous = trend_previous if trend_previous is not None else previous
    counters = current.get("counters", {})
    if (
        current.get("metrics_available", True)
        and isinstance(metrics_previous, dict)
        and metrics_previous.get("metrics_available", True)
        and isinstance(metrics_previous.get("counters"), dict)
    ):
        before = metrics_previous["counters"]
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
                and sum(
                    max(0, counters.get(key, 0) - before.get(key, 0))
                    for key in ("auth.oidc_failure", "auth.local_failure")
                )
                >= 5
            ):
                signal(
                    "authentication_failures",
                    "At least five failed sign-ins since the prior snapshot.",
                )
            if total >= 0 and counters.get("ai.quota_denied", 0) > before.get("ai.quota_denied", 0):
                signal("ai_quota_denials", "AI requests were blocked by the operator quota.")
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


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _application_status(base_url):
    # Operator-only local collector: never follows a response to an external endpoint.
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in {"127.0.0.1", "::1"}
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Collector URL must be a literal loopback HTTP origin")
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    result = {}
    for key, endpoint, timeout in (("available", "/api/health", 1), ("ready", "/api/ready", 5)):
        try:
            with opener.open(Request(base_url.rstrip("/") + endpoint), timeout=timeout) as response:
                payload = json.loads(response.read(4096))
                result[key] = (
                    response.status == 200
                    and isinstance(payload, dict)
                    and payload.get("status") == ("ok" if key == "available" else "ready")
                )
                result[key + "_status"] = response.status
        except HTTPError as exc:
            result[key] = False
            result[key + "_status"] = exc.code
        except (URLError, TimeoutError, OSError, ValueError):
            result[key] = False
            result[key + "_status"] = None
    return result


def collect(base_url, previous=None, trend_previous=None):
    from .operations import report

    snapshot = report()  # Already wall-clock bounded; outage does not require DB aggregates.
    snapshot["application"] = _application_status(base_url)
    snapshot["observed_at"] = datetime.now(timezone.utc).isoformat()
    snapshot["local_alerts"] = evaluate_alerts(snapshot, previous, trend_previous)
    snapshot["external_notifications"] = False
    return snapshot


def watch(base_url, output, samples=0, interval=5):
    if samples < 0 or samples > 3600 or interval < 1 or interval > 3600:
        raise ValueError("Use 0..3600 samples and 1..3600 second interval")
    destination = output.resolve()
    runtime = (Path(__file__).resolve().parents[2] / ".qa-runtime").resolve()
    if not destination.is_relative_to(runtime) or not destination.parent.is_dir():
        raise ValueError("Collector output requires an existing project .qa-runtime directory")
    previous = None
    count = 0
    history = deque(maxlen=128)
    # New files only; fixed-label snapshots never contain account notes or credentials.
    with destination.open("x", encoding="utf-8") as stream:
        while samples == 0 or count < samples:
            now = time.monotonic()
            while history and now - history[0][0] > 60:
                history.popleft()
            baseline = next(
                (row for _, row in history if row.get("metrics_available")),
                {"metrics_available": False},
            )
            snapshot = collect(base_url, previous, baseline)
            if stream.tell() >= 8 * 1024 * 1024:
                raise RuntimeError("Collector reached 8 MiB; rotate to a new private output file")
            stream.write(json.dumps(snapshot) + "\n")
            stream.flush()
            previous = snapshot
            history.append((time.monotonic(), snapshot))
            count += 1
            if samples == 0 or count < samples:
                time.sleep(interval)  # Sequential samples: no overlap or unlimited worker growth.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--current", type=Path)
    mode.add_argument("--watch", action="store_true")
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--url", default="http://127.0.0.1:18018")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--samples", type=int, default=0)
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()
    if args.watch:
        if args.output is None:
            parser.error("--watch requires --output")
        watch(args.url, args.output, args.samples, args.interval)
    else:
        current = json.loads(args.current.read_text(encoding="utf-8"))
        previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
        print(
            json.dumps(
                {"signals": evaluate_alerts(current, previous), "external_notifications": False},
                indent=2,
            )
        )
