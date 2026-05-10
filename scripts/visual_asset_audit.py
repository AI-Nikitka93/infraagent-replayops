from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
MANIFEST = ROOT / "submission_assets" / "visual_assets_manifest.json"
FORBIDDEN = ["linearGradient", "radialGradient", "placeholder", "lorem", "fake live", "stock photo"]


def audit_svg(path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    source = path.read_text(encoding="utf-8")
    for token in FORBIDDEN:
        if token.lower() in source.lower():
            findings.append({"file": str(path.relative_to(ROOT)), "issue": "forbidden_visual_token", "token": token})
    try:
        root = ET.fromstring(source)
    except ET.ParseError as exc:
        return [{"file": str(path.relative_to(ROOT)), "issue": "invalid_svg", "detail": str(exc)}]
    if not root.tag.endswith("svg"):
        findings.append({"file": str(path.relative_to(ROOT)), "issue": "not_svg"})
    if "width" not in root.attrib or "height" not in root.attrib or "viewBox" not in root.attrib:
        findings.append({"file": str(path.relative_to(ROOT)), "issue": "missing_dimensions"})
    if 'role="img"' not in source:
        findings.append({"file": str(path.relative_to(ROOT)), "issue": "missing_img_role"})
    if not re.search(r"<title\b", source):
        findings.append({"file": str(path.relative_to(ROOT)), "issue": "missing_title"})
    if not re.search(r"<desc\b", source):
        findings.append({"file": str(path.relative_to(ROOT)), "issue": "missing_desc"})
    return findings


def main() -> int:
    RUNTIME.mkdir(exist_ok=True)
    findings: list[dict[str, Any]] = []
    if not MANIFEST.is_file():
        findings.append({"file": "submission_assets/visual_assets_manifest.json", "issue": "missing_manifest"})
        manifest: dict[str, Any] = {"assets": []}
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("curation", {}).get("status") != "accepted":
        findings.append({"file": str(MANIFEST.relative_to(ROOT)), "issue": "curation_not_accepted"})
    if manifest.get("style", {}).get("fallback_truth_visible") is not True:
        findings.append({"file": str(MANIFEST.relative_to(ROOT)), "issue": "fallback_truth_not_required"})
    for asset in manifest.get("assets", []):
        rel_path = asset.get("path", "")
        path = ROOT / rel_path
        if asset.get("curation", {}).get("accepted") is not True:
            findings.append({"file": rel_path, "issue": "asset_not_accepted"})
        if not path.is_file():
            findings.append({"file": rel_path, "issue": "missing_asset"})
            continue
        findings.extend(audit_svg(path))
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "asset_count": len(manifest.get("assets", [])),
        "findings": findings,
        "ok": not findings,
    }
    output = RUNTIME / "visual_asset_audit.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
