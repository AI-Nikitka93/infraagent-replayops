from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / ".runtime"
PROOF_FILE = RUNTIME_DIR / "amd_live_proof.json"
VLLM_MODELS_PATH = "/v1/models"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def run_command(command: list[str], timeout: int = 20) -> dict[str, Any]:
    if shutil.which(command[0]) is None:
        return {"command": command, "ok": False, "missing": True, "stdout": "", "stderr": f"{command[0]} not found"}
    completed = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    return {
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def check_device(path: str) -> dict[str, Any]:
    target = Path(path)
    return {"path": path, "exists": target.exists(), "is_char_device_hint": target.exists() and not target.is_file()}


def bearer_headers(token: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_json(url: str, token: str | None = None, timeout: int = 10) -> dict[str, Any]:
    started = time.monotonic()
    try:
        response = requests.get(url, headers=bearer_headers(token), timeout=timeout)
        body: Any
        try:
            body = response.json()
        except Exception:
            body = response.text[:800]
        return {
            "ok": response.ok,
            "status_code": response.status_code,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "body": body,
        }
    except Exception as exc:
        return {"ok": False, "status_code": None, "latency_ms": int((time.monotonic() - started) * 1000), "error": str(exc)}


def post_json(url: str, payload: dict[str, Any], token: str | None = None, timeout: int = 15) -> dict[str, Any]:
    started = time.monotonic()
    try:
        response = requests.post(url, headers=bearer_headers(token), json=payload, timeout=timeout)
        body: Any
        try:
            body = response.json()
        except Exception:
            body = response.text[:800]
        return {
            "ok": response.ok,
            "status_code": response.status_code,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "body": body,
        }
    except Exception as exc:
        return {"ok": False, "status_code": None, "latency_ms": int((time.monotonic() - started) * 1000), "error": str(exc)}


def poll_status(api_base: str, run_id: str, api_key: str, attempts: int, interval: float) -> dict[str, Any]:
    last: dict[str, Any] = {}
    for _ in range(attempts):
        last = get_json(f"{api_base.rstrip('/')}/api/status/{run_id}", api_key, timeout=15)
        body = last.get("body") if isinstance(last.get("body"), dict) else {}
        if body.get("status") in {"ready", "failed", "needs_human_review"}:
            return last
        time.sleep(interval)
    return last


def validate_tunnel_target() -> dict[str, Any]:
    target = os.getenv("CLOUDFLARED_TARGET_URL", "http://localhost:8010")
    raw_vllm_exposed = target.endswith(":8000") or ":8000/" in target
    return {
        "CLOUDFLARED_TARGET_URL": target,
        "ok": target in {"http://localhost:8010", "http://127.0.0.1:8010"},
        "raw_vLLM_exposed": raw_vllm_exposed,
        "note": "Tunnel must expose the agent service on 8010, never raw vLLM on 8000.",
    }


def build_chat_probe_payload(model: str) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise AMD runtime smoke test."},
            {"role": "user", "content": "Return exactly: AMD_QWEN_RUNTIME_OK"},
        ],
        "temperature": 0,
        "max_tokens": 16,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify AMD MI300X/Qwen/vLLM proof for InfraAgent ReplayOps.")
    parser.add_argument("--vllm-base-url", default=os.getenv("VLLM_BASE_URL", "http://127.0.0.1:8000/v1"))
    parser.add_argument("--api-base", default=os.getenv("LANGGRAPH_BASE_URL", "http://127.0.0.1:8010"))
    parser.add_argument("--public-api-base", default=os.getenv("INFRAAGENT_API_BASE", ""))
    parser.add_argument("--model", default=os.getenv("VLLM_SERVED_MODEL_NAME", "qwen2.5-72b-instruct"))
    parser.add_argument("--scenario", default="vllm_saturation")
    parser.add_argument("--poll-attempts", type=int, default=90)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    args = parser.parse_args()

    vllm_api_key = os.getenv("VLLM_API_KEY")
    public_api_key = os.getenv("PUBLIC_API_KEY") or os.getenv("INFRAAGENT_API_KEY")

    proof: dict[str, Any] = {
        "checked_at": now_iso(),
        "host": platform.node(),
        "platform": platform.platform(),
        "target": "AMD Developer Cloud MI300X with ROCm + vLLM + Qwen2.5-72B-Instruct",
        "gpu_runtime": {
            "dev_kfd": check_device("/dev/kfd"),
            "dev_dri": check_device("/dev/dri"),
            "rocminfo": run_command(["rocminfo"], timeout=25),
            "rocm_smi": run_command(["rocm-smi"], timeout=25),
        },
        "tunnel_boundary": validate_tunnel_target(),
        "vllm": {},
        "agent": {},
        "public_agent": {},
        "verdict": "NO_GO_UNTIL_BLOCKERS_CLOSE",
        "blockers": [],
    }

    vllm_base = args.vllm_base_url.rstrip("/")
    models_probe = get_json(f"{vllm_base}/models", vllm_api_key)
    proof["vllm"]["models_endpoint"] = f"{vllm_base}/models"
    proof["vllm"]["models_probe"] = models_probe

    chat_probe = post_json(f"{vllm_base}/chat/completions", build_chat_probe_payload(args.model), vllm_api_key, timeout=60)
    proof["vllm"]["chat_probe"] = chat_probe

    if public_api_key:
        local_base = args.api_base.rstrip("/")
        triage_payload = {
            "service": "qwen-vllm",
            "environment": "amd-mi300x-demo",
            "severity": "major",
            "title": "Agent inference latency spike",
            "description": "AMD rehearsal checks whether Qwen critic and War Room Packet work from live vLLM.",
            "scenario_id": args.scenario,
        }
        start = post_json(f"{local_base}/api/triage", triage_payload, public_api_key)
        proof["agent"]["start"] = start
        run_id = start.get("body", {}).get("run_id") if isinstance(start.get("body"), dict) else None
        if run_id:
            final_status = poll_status(local_base, run_id, public_api_key, args.poll_attempts, args.poll_interval)
            proof["agent"]["final_status"] = final_status

        if args.public_api_base:
            public_base = args.public_api_base.rstrip("/")
            public_start = post_json(f"{public_base}/api/triage", triage_payload, public_api_key)
            proof["public_agent"]["start"] = public_start
            public_run_id = public_start.get("body", {}).get("run_id") if isinstance(public_start.get("body"), dict) else None
            if public_run_id:
                proof["public_agent"]["final_status"] = poll_status(public_base, public_run_id, public_api_key, args.poll_attempts, args.poll_interval)
    else:
        proof["blockers"].append("PUBLIC_API_KEY or INFRAAGENT_API_KEY is required for agent smoke.")

    proof["readiness"] = get_json(f"{args.api_base.rstrip('/')}/api/readiness")

    final_body = proof.get("public_agent", {}).get("final_status", {}).get("body") or proof.get("agent", {}).get("final_status", {}).get("body") or {}
    runtime_mode = (final_body.get("runtime_proof") or {}).get("backend_mode")
    critic_status = ((final_body.get("root_cause") or {}).get("qwen_critic") or {}).get("status")
    packet_present = bool(final_body.get("war_room_packet"))

    checks = {
        "amd_devices": proof["gpu_runtime"]["dev_kfd"]["exists"] and proof["gpu_runtime"]["dev_dri"]["exists"],
        "rocminfo_ok": proof["gpu_runtime"]["rocminfo"].get("ok", False),
        "vllm_models_ok": models_probe.get("ok", False),
        "qwen_chat_ok": chat_probe.get("ok", False),
        "tunnel_agent_only": proof["tunnel_boundary"]["ok"] and not proof["tunnel_boundary"]["raw_vLLM_exposed"],
        "runtime_proof_live_vllm": runtime_mode == "live_vllm",
        "Qwen critic ok": critic_status == "ok",
        "war_room_packet_present": packet_present,
    }
    proof["checks"] = checks
    proof["blockers"].extend([name for name, ok in checks.items() if not ok])
    proof["verdict"] = "GO" if not proof["blockers"] else "NO_GO_UNTIL_BLOCKERS_CLOSE"

    RUNTIME_DIR.mkdir(exist_ok=True)
    PROOF_FILE.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": proof["verdict"], "blockers": proof["blockers"], "proof_file": str(PROOF_FILE)}, indent=2))
    return 0 if proof["verdict"] == "GO" else 2


if __name__ == "__main__":
    sys.exit(main())
