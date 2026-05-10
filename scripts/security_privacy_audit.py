from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
IGNORE_DIRS = {".git", ".runtime", "__pycache__", ".pytest_cache", ".venv", "venv", "env"}
SECRET_PATTERNS = {
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "hf_token": re.compile(r"hf_[A-Za-z0-9]{20,}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    "cloudflare_token": re.compile(r"(?i)cloudflare[_-]?(api)?[_-]?token\\s*=\\s*[^\\s]+"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
}
ALLOWED_TEXT = {
    "CHANGE_ME_PUBLIC_API_KEY",
    "CHANGE_ME_VLLM_API_KEY",
    "sk-YOUR-API-KEY",
}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def scan_file(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    findings: list[dict[str, Any]] = []
    for name, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group(0)
            if value in ALLOWED_TEXT:
                continue
            findings.append({
                "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "type": name,
                "line": text.count("\n", 0, match.start()) + 1,
            })
    return findings


def scan_git_history() -> list[dict[str, Any]]:
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--patch", "--no-color"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:
        return [{"file": "git-history", "type": "history_scan_error", "line": 0, "error": str(exc)}]
    text = result.stdout or ""
    findings: list[dict[str, Any]] = []
    for name, pattern in SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            value = match.group(0)
            if value in ALLOWED_TEXT:
                continue
            findings.append({
                "file": "git-history",
                "type": name,
                "line": text.count("\n", 0, match.start()) + 1,
            })
    return findings


def public_surface_checks() -> dict[str, bool]:
    server = (ROOT / "server.py").read_text(encoding="utf-8")
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    public_state_body = server.split("def public_state", 1)[1].split("def build_submission_readiness", 1)[0]
    return {
        "public_state_filters_audit": '"tool_call_count"' in server and '"trace_id"' in server,
        "public_state_does_not_emit_env": "os.environ" not in public_state_body and "os.getenv" not in public_state_body,
        "bearer_auth_required": "HTTPBearer" in server and "require_api_key" in server,
        "raw_vllm_not_public": "8000" not in app and "VLLM_API_KEY" not in app,
        "runtime_dir_ignored": ".runtime/" in (ROOT / ".gitignore").read_text(encoding="utf-8"),
    }


def main() -> int:
    RUNTIME.mkdir(exist_ok=True)
    findings: list[dict[str, Any]] = []
    for path in iter_files():
        findings.extend(scan_file(path))
    findings.extend(scan_git_history())
    surface = public_surface_checks()
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "findings": findings,
        "public_surface": surface,
        "ok": not findings and all(surface.values()),
    }
    output = RUNTIME / "security_privacy_audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
