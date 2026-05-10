from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
OUTPUT = RUNTIME / "final_submission_gate.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def run_step(name: str, command: list[str], timeout: int, env: dict[str, str] | None = None) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env=env,
    )
    return {
        "name": name,
        "command": command,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-6000:],
        "stderr_tail": completed.stderr[-6000:],
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def append_public_smoke_args(command: list[str], args: argparse.Namespace) -> list[str]:
    public_command = [*command, "--api-base", args.api_base]
    if args.api_key:
        public_command.extend(["--api-key", args.api_key])
    if args.api_key_file:
        public_command.extend(["--api-key-file", args.api_key_file])
    if args.space_host:
        public_command.extend(["--space-host", args.space_host])
    return public_command


def load_gate_api_key(args: argparse.Namespace) -> str:
    if args.api_key:
        return args.api_key.strip()
    if args.api_key_file:
        return (ROOT / args.api_key_file).read_text(encoding="utf-8").strip()
    return os.getenv("PUBLIC_API_KEY", "").strip() or os.getenv("INFRAAGENT_API_KEY", "").strip()


def build_blockers(
    steps: list[dict[str, Any]],
    amd_proof: dict[str, Any],
    public_smoke: dict[str, Any],
    public_smoke_required: bool,
) -> list[str]:
    blockers = [f"step_failed:{step['name']}" for step in steps if not step["ok"] and step["name"] != "amd_runtime_rehearsal"]

    amd_checks = amd_proof.get("checks") or {}
    required_amd_checks = [
        "amd_devices",
        "rocminfo_ok",
        "vllm_models_ok",
        "qwen_chat_ok",
        "tunnel_agent_only",
        "runtime_proof_live_vllm",
        "Qwen critic ok",
        "war_room_packet_present",
    ]
    for check in required_amd_checks:
        if amd_checks.get(check) is not True:
            blockers.append(f"amd_proof_missing:{check}")

    if amd_proof.get("verdict") != "GO":
        blockers.append("amd_runtime_rehearsal_not_go")

    if public_smoke_required:
        if not public_smoke:
            blockers.append("public_smoke_not_run")
        elif public_smoke.get("ok") is not True:
            blockers.append("public_smoke_not_ok")
        api = public_smoke.get("api") or {}
        readiness = api.get("readiness") or {}
        checks = (readiness.get("external_submission") or {}).get("checks") or {}
        if checks.get("qwen_critic_ok") is not True:
            blockers.append("qwen_critic_ok_not_publicly_observed")
        if readiness.get("verdict") != "GO":
            blockers.append("public_readiness_not_go")

    return sorted(set(blockers))


def main() -> int:
    parser = argparse.ArgumentParser(description="Final blocking gate for AMD Developer Hackathon submission.")
    parser.add_argument("--api-base", default="")
    parser.add_argument("--api-key", default="")
    parser.add_argument("--api-key-file", default="")
    parser.add_argument("--space-host", default="")
    parser.add_argument("--skip-public-smoke", action="store_true")
    args = parser.parse_args()

    RUNTIME.mkdir(exist_ok=True)
    steps: list[dict[str, Any]] = []
    gate_api_key = load_gate_api_key(args)
    step_env = os.environ.copy()
    if gate_api_key:
        step_env["PUBLIC_API_KEY"] = gate_api_key
        step_env["INFRAAGENT_API_KEY"] = gate_api_key
    local_commands = [
        ("pytest", [sys.executable, "-m", "pytest", "-q"], 240),
        (
            "compileall",
            [
                sys.executable,
                "-m",
                "compileall",
                "agent.py",
                "tools.py",
                "server.py",
                "app.py",
                "scripts\\amd_runtime_rehearsal.py",
                "scripts\\refresh_public_demo.py",
                "scripts\\public_smoke.py",
                "scripts\\security_privacy_audit.py",
                "scripts\\claim_audit.py",
                "scripts\\visual_asset_audit.py",
                "scripts\\final_submission_gate.py",
            ],
            120,
        ),
        ("claim_audit", [sys.executable, "scripts\\claim_audit.py"], 60),
        ("security_privacy_audit", [sys.executable, "scripts\\security_privacy_audit.py"], 60),
        ("visual_asset_audit", [sys.executable, "scripts\\visual_asset_audit.py"], 60),
        ("amd_runtime_rehearsal", [sys.executable, "scripts\\amd_runtime_rehearsal.py"], 240),
    ]

    for name, command, timeout in local_commands:
        steps.append(run_step(name, command, timeout, step_env))

    public_smoke_required = not args.skip_public_smoke and bool(args.api_base)
    if public_smoke_required:
        command = append_public_smoke_args([sys.executable, "scripts\\public_smoke.py"], args)
        steps.append(run_step("public_smoke", command, 240, step_env))

    amd_proof = load_json(RUNTIME / "amd_live_proof.json")
    public_smoke = load_json(RUNTIME / "public_smoke_status.json") if public_smoke_required else {}
    blockers = build_blockers(steps, amd_proof, public_smoke, public_smoke_required)
    verdict = "GO_SUBMIT" if not blockers else "NO_GO_UNTIL_BLOCKERS_CLOSE"
    report = {
        "checked_at": now_iso(),
        "verdict": verdict,
        "blockers": blockers,
        "steps": steps,
        "amd_proof_file": str(RUNTIME / "amd_live_proof.json"),
        "public_smoke_file": str(RUNTIME / "public_smoke_status.json") if public_smoke_required else None,
        "requirements": {
            "live_vllm": "runtime_proof.backend_mode must be live_vllm in a public run.",
            "qwen_critic_ok": "Root-cause panel must show Qwen critic status ok.",
            "amd_runtime_evidence": "Runtime proof must include amd_runtime_evidence.ok=true.",
            "readiness": "Public readiness verdict must be GO before final submission.",
        },
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "blockers": blockers, "proof_file": str(OUTPUT)}, ensure_ascii=False, indent=2))
    return 0 if verdict == "GO_SUBMIT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
