from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"


def http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
    expect_error: int | None = None,
) -> Any:
    body = None
    req_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, method=method, headers=req_headers)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            data = response.read().decode("utf-8")
            return json.loads(data) if data else {"status_code": response.status}
    except error.HTTPError as exc:
        if expect_error == exc.code:
            return {"status_code": exc.code, "body": exc.read().decode("utf-8", errors="replace")}
        raise


def read_api_key(args: argparse.Namespace) -> str:
    if args.api_key:
        return args.api_key
    if args.api_key_file:
        return (ROOT / args.api_key_file).read_text(encoding="utf-8").strip()
    value = os.getenv("PUBLIC_API_KEY") or os.getenv("INFRAAGENT_API_KEY")
    if not value:
        raise RuntimeError("PUBLIC_API_KEY, INFRAAGENT_API_KEY, --api-key, or --api-key-file is required.")
    return value.strip()


def smoke_api(base_url: str, api_key: str, scenario_id: str) -> dict[str, Any]:
    base = base_url.rstrip("/")
    good_headers = {"Authorization": f"Bearer {api_key}"}
    health = http_json(f"{base}/health", timeout=10)
    readiness = http_json(f"{base}/api/readiness", timeout=20)
    missing_bearer = http_json(f"{base}/api/triage", method="POST", payload={"scenario_id": scenario_id}, expect_error=401)
    wrong_bearer = http_json(
        f"{base}/api/triage",
        method="POST",
        headers={"Authorization": "Bearer wrong bearer"},
        payload={"scenario_id": scenario_id},
        expect_error=403,
    )
    accepted = http_json(
        f"{base}/api/triage",
        method="POST",
        headers=good_headers,
        payload={
            "alert_payload": "Public smoke alert: checkout-api elevated 5xx after deploy",
            "scenario_id": scenario_id,
        },
        timeout=30,
    )
    run_id = accepted["run_id"]
    status_payload: dict[str, Any] = {}
    for _ in range(60):
        status_payload = http_json(f"{base}/api/status/{run_id}", headers=good_headers, timeout=20)
        if status_payload.get("status") in {"ready", "failed", "needs_human_review"}:
            break
        time.sleep(1)
    return {
        "health": health,
        "readiness": readiness,
        "auth": {
            "missing_bearer": missing_bearer["status_code"],
            "wrong_bearer": wrong_bearer["status_code"],
        },
        "run_id": run_id,
        "status": status_payload.get("status"),
        "score": (status_payload.get("eval_scorecard") or {}).get("score"),
        "runtime_mode": (status_payload.get("runtime_proof") or {}).get("backend_mode"),
        "qwen_critic": ((status_payload.get("root_cause") or {}).get("qwen_critic") or {}).get("status"),
        "packet": bool(status_payload.get("war_room_packet")),
        "errors": status_payload.get("errors", []),
    }


def smoke_space(space_host: str) -> dict[str, Any]:
    if not space_host:
        return {"skipped": True, "reason": "space host not provided"}
    try:
        from gradio_client import Client
    except ImportError:
        return {"skipped": True, "reason": "gradio_client not installed"}
    client = Client(space_host)
    job = client.submit(
        "Public smoke alert: checkout-api elevated 5xx after deploy",
        "checkout_deploy_regression",
        api_name="/run_triage",
    )
    result = job.result(timeout=120)
    stream = "\n".join(str(part) for part in result)
    return {
        "ready": "READY" in stream or "status-ready" in stream,
        "score_100": "Score: 100/100" in stream,
        "fallback_visible": "fallback_without_live_vllm" in stream,
        "live_vllm_visible": "Observed backend:** `live_vllm`" in stream or "Observed backend:</strong> `live_vllm`" in stream,
        "network_error": "Network or API error" in stream,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test public InfraAgent API and optional HF Space.")
    parser.add_argument("--api-base", required=True)
    parser.add_argument("--api-key")
    parser.add_argument("--api-key-file")
    parser.add_argument("--space-host", default="")
    parser.add_argument("--scenario-id", default="checkout_deploy_regression")
    args = parser.parse_args()

    RUNTIME.mkdir(exist_ok=True)
    report: dict[str, Any] = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "api_base": args.api_base,
        "space_host": args.space_host,
    }
    try:
        api_key = read_api_key(args)
        report["api"] = smoke_api(args.api_base, api_key, args.scenario_id)
        report["space"] = smoke_space(args.space_host)
        api = report["api"]
        report["ok"] = (
            api.get("status") in {"ready", "needs_human_review"}
            and api.get("score") is not None
            and api.get("packet") is True
            and api.get("auth", {}).get("missing_bearer") == 401
            and api.get("auth", {}).get("wrong_bearer") == 403
        )
    except Exception as exc:
        report["ok"] = False
        report["error"] = str(exc)
    output = RUNTIME / "public_smoke_status.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
