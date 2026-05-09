from pathlib import Path


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
