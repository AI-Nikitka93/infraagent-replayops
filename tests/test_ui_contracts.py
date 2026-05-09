from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_file(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_ui_files_exist() -> None:
    assert (ROOT / "requirements-ui.txt").is_file()
    assert (ROOT / "app.py").is_file()


def test_app_uses_hf_space_env_and_bearer_auth() -> None:
    source = read_file("app.py")
    assert "INFRAAGENT_API_BASE" in source
    assert "INFRAAGENT_API_KEY" in source
    assert "Authorization" in source
    assert "Bearer" in source
    assert "localhost" not in source.lower()
    assert "127.0.0.1" not in source


def test_app_uses_polling_contract_without_streaming_transports() -> None:
    source = read_file("app.py")
    assert "/api/triage" in source
    assert "/api/status/" in source
    assert "MAX_POLL_ATTEMPTS" in source
    assert "time.sleep" in source
    assert "yield" in source
    assert "WebSocket" not in source
    assert "EventSource" not in source


def test_app_surfaces_replayops_panels() -> None:
    source = read_file("app.py")
    for label in [
        "Eval Scorecard",
        "Live Agent Trace",
        "Evidence Timeline",
        "Runtime proof",
        "War Room Packet",
        "Business / Ownership Lens",
        "Submission Readiness",
    ]:
        assert label in source


def test_app_separates_target_stack_from_observed_runtime() -> None:
    source = read_file("app.py")
    assert "Observed backend" in source
    assert "Target AMD stack" in source
    assert "hardware_claim" not in source


def test_requirements_ui_are_minimal() -> None:
    source = read_file("requirements-ui.txt")
    assert "gradio" in source
    assert "requests" in source
