from __future__ import annotations

import argparse
import contextlib
import http.client
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
DEFAULT_SPACE_ID = "clendeningantonettie/infraagent-replayops"
DEFAULT_SPACE_HOST = "https://clendeningantonettie-infraagent-replayops.hf.space"


def now_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def http_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, payload: dict[str, Any] | None = None, timeout: int = 30) -> Any:
    body = None
    req_headers = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, method=method, headers=req_headers)
    with request.urlopen(req, timeout=timeout) as response:
        data = response.read().decode("utf-8")
    return json.loads(data) if data else None


def http_text(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None, timeout: int = 90) -> str:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, method=method, headers=headers)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except http.client.IncompleteRead as exc:
        partial = exc.partial or b""
        return partial.decode("utf-8", errors="replace")


def find_cloudflared() -> str:
    local = ROOT / ".runtime" / "bin" / ("cloudflared.exe" if os.name == "nt" else "cloudflared")
    if local.exists():
        return str(local)
    return "cloudflared"


def ensure_backend(base_url: str) -> dict[str, Any]:
    return http_json(f"{base_url.rstrip('/')}/health", timeout=10)


def launch_tunnel(target_url: str, protocol: str) -> tuple[subprocess.Popen[Any], str, Path]:
    RUNTIME.mkdir(exist_ok=True)
    stamp = now_slug()
    log_path = RUNTIME / f"cloudflared-refresh-{stamp}.err.log"
    out_path = RUNTIME / f"cloudflared-refresh-{stamp}.out.log"
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    err_handle = log_path.open("w", encoding="utf-8")
    out_handle = out_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [find_cloudflared(), "tunnel", "--protocol", protocol, "--url", target_url],
        cwd=ROOT,
        stdout=out_handle,
        stderr=err_handle,
        creationflags=creationflags,
    )

    public_url = ""
    deadline = time.time() + 90
    pattern = re.compile(r"https://[-a-z0-9]+\.trycloudflare\.com")
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"cloudflared exited early; see {log_path}")
        if log_path.exists():
            match = pattern.search(log_path.read_text(encoding="utf-8", errors="replace"))
            if match:
                public_url = match.group(0)
                break
        time.sleep(1)
    if not public_url:
        raise TimeoutError(f"Timed out waiting for Quick Tunnel URL in {log_path}")

    return process, public_url, log_path


def record_active_tunnel(public_url: str, process: subprocess.Popen[Any] | None = None, log_path: Path | None = None) -> None:
    if process is not None:
        (RUNTIME / "cloudflared-active.pid").write_text(str(process.pid), encoding="utf-8")
    if log_path is not None:
        (RUNTIME / "cloudflared-active-log.txt").write_text(str(log_path), encoding="utf-8")
    (RUNTIME / "public_api_url.txt").write_text(public_url, encoding="utf-8")


def stop_process(process: subprocess.Popen[Any]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def wait_for_public_health(public_url: str, seconds: int) -> dict[str, Any]:
    deadline = time.time() + seconds
    last_error = ""
    while time.time() < deadline:
        try:
            return http_json(f"{public_url.rstrip('/')}/health", timeout=15)
        except (TimeoutError, OSError, error.URLError) as exc:
            last_error = str(exc)
            time.sleep(5)
    raise TimeoutError(f"Public tunnel did not become reachable: {last_error}")


def launch_reachable_tunnel(target_url: str, protocol: str, attempts: int, health_wait_seconds: int) -> tuple[subprocess.Popen[Any], str, Path, dict[str, Any]]:
    errors: list[str] = []
    for attempt in range(1, attempts + 1):
        process, public_url, log_path = launch_tunnel(target_url, protocol)
        try:
            health = wait_for_public_health(public_url, health_wait_seconds)
            record_active_tunnel(public_url, process=process, log_path=log_path)
            return process, public_url, log_path, health
        except Exception as exc:
            errors.append(f"attempt {attempt}: {public_url}: {exc}")
            stop_process(process)
    raise RuntimeError("Could not create a reachable Quick Tunnel. " + " | ".join(errors))


def smoke_public_api(public_url: str, api_key: str) -> dict[str, Any]:
    base = public_url.rstrip("/")
    headers = {"Authorization": f"Bearer {api_key}"}
    health = wait_for_public_health(base, seconds=60)
    readiness = http_json(f"{base}/api/readiness")
    accepted = http_json(
        f"{base}/api/triage",
        method="POST",
        headers=headers,
        payload={
            "alert_payload": "PagerDuty alert: checkout-api elevated 5xx after deploy",
            "scenario_id": "checkout_deploy_regression",
        },
    )
    run_id = accepted["run_id"]
    status_payload: dict[str, Any] = {}
    for _ in range(20):
        status_payload = http_json(f"{base}/api/status/{run_id}", headers=headers)
        if status_payload.get("status") in {"ready", "failed", "needs_human_review"}:
            break
        time.sleep(1)
    return {
        "health": health,
        "readiness": readiness,
        "run_id": run_id,
        "status": status_payload.get("status"),
        "score": (status_payload.get("eval_scorecard") or {}).get("score"),
        "runtime_mode": (status_payload.get("runtime_proof") or {}).get("backend_mode"),
        "qwen_critic": ((status_payload.get("root_cause") or {}).get("qwen_critic") or {}).get("status"),
        "packet": bool(status_payload.get("war_room_packet")),
    }


def update_hf_space(space_id: str, public_url: str, api_key: str) -> None:
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is required to update HF Space secrets") from exc
    api = HfApi()
    api.add_space_secret(repo_id=space_id, key="INFRAAGENT_API_BASE", value=public_url)
    api.add_space_secret(repo_id=space_id, key="INFRAAGENT_API_KEY", value=api_key)


def smoke_hf_space(space_host: str) -> dict[str, Any]:
    try:
        from gradio_client import Client

        with contextlib.redirect_stdout(io.StringIO()):
            client = Client(space_host)
            job = client.submit(
                "PagerDuty alert: checkout-api is serving elevated 5xx responses after the latest deployment.",
                "checkout_deploy_regression",
                api_name="/run_triage",
            )
            result = job.result(timeout=120)
        stream = "\n".join(str(part) for part in result)
        return {
            "event_id": "gradio_client",
            "ready": "status-ready" in stream or "READY" in stream,
            "score_100": "Score: 100/100" in stream,
            "fallback_visible": "fallback_without_live_vllm" in stream,
            "live_vllm_visible": "Observed backend:** `live_vllm`" in stream or "Observed backend:</strong> `live_vllm`" in stream,
            "network_error": "Network or API error" in stream,
        }
    except ImportError:
        pass

    call = http_json(
        f"{space_host.rstrip('/')}/gradio_api/call/run_triage",
        method="POST",
        payload={
            "data": [
                "PagerDuty alert: checkout-api is serving elevated 5xx responses after the latest deployment.",
                "checkout_deploy_regression",
            ]
        },
        timeout=45,
    )
    event_id = call["event_id"]
    stream = ""
    deadline = time.time() + 120
    event_url = f"{space_host.rstrip('/')}/gradio_api/call/run_triage/{event_id}"
    while time.time() < deadline:
        try:
            latest = http_text(event_url, timeout=60)
            if latest:
                stream = latest
        except error.HTTPError as exc:
            stream = f"HTTP {exc.code}: {exc.reason}"
        if any(marker in stream for marker in ["status-ready", "READY", "Network or API error", "event: complete"]):
            break
        time.sleep(5)
    return {
        "event_id": event_id,
        "ready": "status-ready" in stream or "READY" in stream,
        "score_100": "Score: 100/100" in stream,
        "fallback_visible": "fallback_without_live_vllm" in stream,
        "live_vllm_visible": "Observed backend:** `live_vllm`" in stream or "Observed backend:</strong> `live_vllm`" in stream,
        "network_error": "Network or API error" in stream,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh and smoke-test the public InfraAgent demo path.")
    parser.add_argument("--backend-base", default="http://127.0.0.1:8010")
    parser.add_argument("--tunnel-target", default="http://127.0.0.1:8010")
    parser.add_argument("--protocol", default="http2")
    parser.add_argument("--max-tunnel-attempts", type=int, default=4)
    parser.add_argument("--public-health-wait-seconds", type=int, default=45)
    parser.add_argument("--api-key-file", default=".runtime/local_api_key.txt")
    parser.add_argument("--space-id", default=DEFAULT_SPACE_ID)
    parser.add_argument("--space-host", default=DEFAULT_SPACE_HOST)
    parser.add_argument("--update-hf-space", action="store_true")
    parser.add_argument("--smoke-space", action="store_true")
    parser.add_argument("--force-new-tunnel", action="store_true")
    args = parser.parse_args()

    status: dict[str, Any] = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "backend_base": args.backend_base,
        "space_id": args.space_id,
        "space_host": args.space_host,
    }
    api_key = read_text(ROOT / args.api_key_file)
    try:
        status["local_health"] = ensure_backend(args.backend_base)
        current_url_path = RUNTIME / "public_api_url.txt"
        current_url = read_text(current_url_path) if current_url_path.exists() else ""
        process = None
        log_path = None
        if current_url and not args.force_new_tunnel:
            try:
                health = wait_for_public_health(current_url, seconds=10)
                public_url = current_url
                status["reused_current_tunnel"] = True
            except Exception:
                process, public_url, log_path, health = launch_reachable_tunnel(
                    args.tunnel_target,
                    args.protocol,
                    args.max_tunnel_attempts,
                    args.public_health_wait_seconds,
                )
                status["reused_current_tunnel"] = False
        else:
            process, public_url, log_path, health = launch_reachable_tunnel(
                args.tunnel_target,
                args.protocol,
                args.max_tunnel_attempts,
                args.public_health_wait_seconds,
            )
            status["reused_current_tunnel"] = False
        if process is not None:
            status["cloudflared_pid"] = process.pid
        if log_path is not None:
            status["cloudflared_log"] = str(log_path)
        status["public_api_url"] = public_url
        status["public_health"] = health
        status["public_api"] = smoke_public_api(public_url, api_key)
        public_api = status["public_api"]
        if public_api.get("status") != "ready" or public_api.get("score") != 100 or not public_api.get("packet"):
            raise RuntimeError(f"Public API smoke failed: {public_api}")
        if args.update_hf_space:
            update_hf_space(args.space_id, public_url, api_key)
            status["hf_space_secrets_updated"] = True
        if args.smoke_space:
            time.sleep(20)
            status["hf_space"] = smoke_hf_space(args.space_host)
            hf_space = status["hf_space"]
            if not hf_space.get("ready") or not hf_space.get("score_100") or hf_space.get("network_error"):
                raise RuntimeError(f"HF Space smoke failed: {hf_space}")
        status["ok"] = True
    except Exception as exc:
        status["ok"] = False
        status["error"] = str(exc)
    finally:
        write_json(RUNTIME / "public_demo_status.json", status)

    print(json.dumps(status, indent=2, sort_keys=True))
    return 0 if status.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
