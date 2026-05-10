from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


def read_file(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_submission_required_artifacts_exist() -> None:
    for name in ["LICENSE", "SUBMISSION.md", "DEMO_SCRIPT.md", "SLIDES.md", "HACKATHON_READINESS.md"]:
        assert (ROOT / name).is_file(), f"{name} is missing"


def test_submission_copy_is_honest_about_live_runtime_requirements() -> None:
    submission = read_file("SUBMISSION.md")
    readiness = read_file("HACKATHON_READINESS.md")
    assert "fallback_without_live_vllm" in submission
    assert "live_vllm" in submission
    assert "mock observability fixtures" in submission
    assert "AMD MI300X" in submission
    assert "HF Space URL" in readiness
    assert "Public GitHub" in readiness
    assert "Links To Fill" not in submission
    assert "must be inserted before final submission" not in submission


def test_market_research_is_captured_for_judges() -> None:
    research = read_file("docs/market-pain-map.md")
    for text in ["alert fatigue", "tool sprawl", "ownership", "mttr", "agentic observability"]:
        assert text in research.lower()


def test_public_demo_refresh_script_exists_and_preserves_secret_boundary() -> None:
    script = read_file("scripts/refresh_public_demo.py")
    assert "add_space_secret" in script
    assert "public_demo_status.json" in script
    assert "gradio_api/call/run_triage" in script
    assert "INFRAAGENT_API_KEY" in script
    assert "print(api_key)" not in script


def test_contest_truth_snapshot_is_current_and_track_one_focused() -> None:
    snapshot = read_file("docs/contest_truth.json")
    for text in [
        '"checked_at": "2026-05-10"',
        '"selected_track": "Track 1: AI Agents & Agentic Workflows"',
        '"Application of Technology"',
        '"Presentation"',
        '"Business Value"',
        '"Originality"',
        '"Build in Public"',
        '"live_vllm"',
    ]:
        assert text in snapshot


def test_runtime_rehearsal_script_checks_amd_gpu_vllm_and_tunnel_boundary() -> None:
    script = read_file("scripts/amd_runtime_rehearsal.py")
    for text in [
        "rocminfo",
        "/dev/kfd",
        "/dev/dri",
        "/v1/models",
        "/api/triage",
        "/api/status/",
        "runtime_proof",
        "Qwen critic",
        "CLOUDFLARED_TARGET_URL",
        "8010",
    ]:
        assert text in script
    assert "8000" in script
    assert "raw vLLM" in script


def test_judge_materials_expose_gap_and_artifacts_to_update_after_live_proof() -> None:
    readme = read_file("README.md")
    submission = read_file("SUBMISSION.md")
    readiness = read_file("HACKATHON_READINESS.md")
    for text in [
        "fallback demo verified, live AMD/Qwen proof pending",
        "Artifacts to refresh after live AMD proof",
        "named Cloudflare Tunnel",
        "scripts/final_submission_gate.py",
        "GO_SUBMIT",
    ]:
        assert text in readme
        assert text in submission
        assert text in readiness


def test_visual_asset_manifest_and_curated_assets_are_release_ready() -> None:
    manifest_path = ROOT / "submission_assets" / "visual_assets_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["style"]["direction"] == "operational war-room"
    assert manifest["style"]["fallback_truth_visible"] is True
    assert manifest["curation"]["status"] == "accepted"
    assert len(manifest["assets"]) >= 3
    for asset in manifest["assets"]:
        path = ROOT / asset["path"]
        assert path.is_file(), f"{path} is missing"
        source = path.read_text(encoding="utf-8")
        assert "<svg" in source
        assert "linearGradient" not in source
        assert "placeholder" not in source.lower()
        assert asset["curation"]["accepted"] is True


def test_submission_story_contains_faq_comparison_amd_and_contingency_sections() -> None:
    submission = read_file("SUBMISSION.md")
    readme = read_file("README.md")
    faq = read_file("docs/JUDGE_FAQ.md")
    build = read_file("docs/BUILD_IN_PUBLIC.md")
    for text in [
        "Judge FAQ",
        "Why AMD Matters",
        "Not A Generic Incident Assistant",
        "Contingency Wording",
    ]:
        assert text in submission
        assert text in readme
    for text in ["what is live", "what is mocked", "human-approved", "auto-remediation"]:
        assert text in faq.lower()
    for text in ["ROCm", "AMD Developer Cloud", "vLLM/Qwen", "Cloudflare Tunnel"]:
        assert text in build


def test_security_recovery_and_judging_scripts_exist() -> None:
    for name in [
        "scripts/security_privacy_audit.py",
        "scripts/claim_audit.py",
        "scripts/visual_asset_audit.py",
        "scripts/public_smoke.py",
        "scripts/final_submission_gate.py",
        "docs/RECOVERY_CHECKLIST.md",
        "docs/JUDGING_DAY_RUNBOOK.md",
    ]:
        assert (ROOT / name).is_file(), f"{name} is missing"
    security = read_file("scripts/security_privacy_audit.py")
    assert "SECRET_PATTERNS" in security
    assert ".runtime" in security
    assert "public_state" in security
    public_smoke = read_file("scripts/public_smoke.py")
    assert "/api/readiness" in public_smoke
    assert "/api/triage" in public_smoke
    assert "wrong bearer" in public_smoke.lower()
    claim_audit = read_file("scripts/claim_audit.py")
    assert "fallback demo verified, live AMD/Qwen proof pending" in claim_audit
    assert "live_vllm" in claim_audit
    visual_audit = read_file("scripts/visual_asset_audit.py")
    assert "visual_assets_manifest.json" in visual_audit
    assert "linearGradient" in visual_audit
    assert "title" in visual_audit
    final_gate = read_file("scripts/final_submission_gate.py")
    assert "GO_SUBMIT" in final_gate
    assert "NO_GO_UNTIL_BLOCKERS_CLOSE" in final_gate
    assert "amd_runtime_rehearsal.py" in final_gate
    assert "public_smoke.py" in final_gate
    assert "final_submission_gate.json" in final_gate
    assert "qwen_critic_ok" in final_gate
    assert "PUBLIC_API_KEY" in final_gate
    assert "load_gate_api_key" in final_gate
