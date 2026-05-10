from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
MATERIALS = [
    "README.md",
    "SUBMISSION.md",
    "HACKATHON_READINESS.md",
    "DEMO_SCRIPT.md",
    "SLIDES.md",
    "docs/STATE.md",
    "docs/JUDGE_FAQ.md",
    "docs/BUILD_IN_PUBLIC.md",
    "docs/RECOVERY_CHECKLIST.md",
    "docs/JUDGING_DAY_RUNBOOK.md",
]
REQUIRED_PHRASES = [
    "fallback demo verified, live AMD/Qwen proof pending",
    "live_vllm",
    "fallback_without_live_vllm",
    "mock observability",
    "human approval",
]
FORBIDDEN_PHRASES = [
    "production telemetry is live",
    "auto-remediation is enabled",
    "Qwen critic: ok in fallback",
    "readiness verdict is GO",
]


def main() -> int:
    RUNTIME.mkdir(exist_ok=True)
    findings: list[dict[str, Any]] = []
    for name in MATERIALS:
        path = ROOT / name
        if not path.is_file():
            findings.append({"file": name, "issue": "missing"})
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lowered:
                findings.append({"file": name, "issue": "forbidden_claim", "phrase": phrase})
    combined = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in MATERIALS if (ROOT / name).is_file())
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in combined.lower():
            findings.append({"file": "combined", "issue": "missing_required_truth_phrase", "phrase": phrase})
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "materials": MATERIALS,
        "findings": findings,
        "ok": not findings,
    }
    (RUNTIME / "claim_audit.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
