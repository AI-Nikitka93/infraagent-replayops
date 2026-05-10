import asyncio
from pathlib import Path
import sys

from fastapi import HTTPException
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def read_file(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_required_backend_files_exist() -> None:
    for name in ["requirements.txt", "tools.py", "agent.py", "server.py"]:
        assert (ROOT / name).is_file(), f"{name} is missing"


def test_agent_uses_vllm_environment_and_recursion_limit() -> None:
    source = read_file("agent.py")
    assert 'os.getenv("VLLM_BASE_URL"' in source
    assert 'os.getenv("VLLM_API_KEY"' in source
    assert "recursion_limit" in source
    assert "StateGraph" in source
    assert "MemorySaver" in source


def test_server_uses_polling_api_auth_and_port_8010() -> None:
    source = read_file("server.py")
    assert '@app.post("/api/triage"' in source
    assert '@app.get("/api/status/{run_id}"' in source
    assert "Authorization" in source
    assert 'host="127.0.0.1"' in source
    assert "port=8010" in source
    assert "websocket" not in source.lower()
    assert "EventSource" not in source
    assert "text/event-stream" not in source
    assert 'os.getenv("PUBLIC_API_KEY", "CHANGE_ME_PUBLIC_API_KEY")' not in source
    assert "validate_public_api_key" in source


def test_public_api_key_rejects_missing_or_placeholder_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PUBLIC_API_KEY", raising=False)
    import server

    with pytest.raises(HTTPException):
        server.validate_public_api_key()

    monkeypatch.setenv("PUBLIC_API_KEY", "CHANGE_ME_PUBLIC_API_KEY")
    with pytest.raises(HTTPException):
        server.validate_public_api_key()

    monkeypatch.setenv("PUBLIC_API_KEY", "real-secret")
    assert server.validate_public_api_key() == "real-secret"


def test_tools_have_realistic_mock_contracts() -> None:
    source = read_file("tools.py")
    assert "@tool" in source
    assert "get_recent_logs" in source
    assert "get_metric_anomaly" in source
    assert "get_deploy_events" in source
    assert "get_service_topology" in source
    assert "evaluate_triage" in source
    assert "evidence_id" in source


def test_backend_exposes_replayops_fields() -> None:
    agent_source = read_file("agent.py")
    server_source = read_file("server.py")
    for field in ["runtime_proof", "eval_scorecard", "war_room_packet", "node_traces", "evidence_items"]:
        assert field in agent_source
        assert field in server_source


def test_backend_exposes_runtime_truth_and_readiness_gate() -> None:
    agent_source = read_file("agent.py")
    server_source = read_file("server.py")
    assert "target_hardware" in agent_source
    assert "observed_hardware" in agent_source
    assert "runtime_truth" in agent_source
    assert '@app.get("/api/readiness"' in server_source
    assert "submission_readiness" in server_source
    assert "formal_blockers" in server_source
    assert "contest_truth" in server_source
    assert "live_proof_requirements" in server_source


def test_probe_runtime_does_not_count_vllm_without_amd_device_proof(monkeypatch: pytest.MonkeyPatch) -> None:
    import agent

    class FakeModelsResponse:
        ok = True
        status_code = 200
        text = "{}"

        @staticmethod
        def json() -> dict:
            return {"data": [{"id": "qwen2.5-72b-instruct"}]}

    monkeypatch.setattr(agent.requests, "get", lambda *args, **kwargs: FakeModelsResponse())
    monkeypatch.setattr(agent, "detect_amd_runtime_evidence", lambda: {"ok": False, "signals": []})

    proof = agent.probe_runtime()

    assert proof["backend_mode"] == "runtime_unhealthy"
    assert proof["healthy"] is False
    assert proof["amd_runtime_evidence"]["ok"] is False
    assert "AMD runtime proof is missing" in proof["runtime_truth"]


def test_readiness_requires_qwen_critic_ok_before_go(monkeypatch: pytest.MonkeyPatch) -> None:
    import server

    for name in ["HF_SPACE_URL", "PUBLIC_REPO_URL", "DEMO_VIDEO_URL", "SLIDE_DECK_URL"]:
        monkeypatch.setenv(name, f"https://example.com/{name.lower()}")

    readiness = server.build_submission_readiness(
        {"backend_mode": "live_vllm"},
        {"qwen_critic": {"status": "skipped"}},
    )

    assert readiness["external_submission"]["checks"]["qwen_critic_ok"] is False
    assert "qwen_critic_ok" in readiness["formal_blockers"]
    assert readiness["verdict"] == "NO_GO_UNTIL_BLOCKERS_CLOSE"


def test_server_keeps_agent_runtime_lazy_for_health_and_readiness() -> None:
    source = read_file("server.py")
    assert "from agent import" not in source
    assert "def load_agent_runtime" in source
    assert "load_agent_runtime()" in source


def test_agent_suppresses_known_langgraph_serializer_warning() -> None:
    source = read_file("agent.py")
    assert "LangChainPendingDeprecationWarning" in source
    assert "warnings.filterwarnings" in source


def test_backend_surfaces_market_pain_and_ownership_lens() -> None:
    tools_source = read_file("tools.py")
    agent_source = read_file("agent.py")
    for text in ["pain_profile", "ownership_hint", "business_risk", "manual_triage_baseline_minutes"]:
        assert text in tools_source
        assert text in agent_source


def test_langgraph_pipeline_stays_within_five_nodes() -> None:
    source = read_file("agent.py")
    assert source.count("builder.add_node(") == 5


def test_scenarios_include_story_fields_and_negative_case() -> None:
    from tools import SCENARIOS, scenario_metadata

    assert "insufficient_evidence_unknown_outage" in SCENARIOS
    incident_types = {scenario["incident_type"] for scenario in SCENARIOS.values()}
    assert len(incident_types) >= 6
    for scenario_id in SCENARIOS:
        metadata = scenario_metadata(scenario_id)
        for field in [
            "symptom",
            "service_owner",
            "business_risk",
            "evidence_trail",
            "recovery_summary",
            "communication_targets",
            "post_recovery_checks",
            "fixture_truth_note",
        ]:
            assert metadata[field]


def test_negative_case_goes_to_human_review_without_confident_root_cause() -> None:
    from agent import create_initial_state, run_triage

    state = create_initial_state("negative-smoke", {"scenario_id": "insufficient_evidence_unknown_outage"})
    result = asyncio.run(run_triage(state, "negative-smoke"))
    assert result["status"] == "needs_human_review"
    assert result["root_cause"]["confidence"] == "low"
    assert result["root_cause"]["supporting_evidence_ids"] == []
    assert result["eval_scorecard"]["grade"] == "review"


def test_war_room_packet_acceptance_contract_is_encoded() -> None:
    source = read_file("agent.py")
    for section in [
        "## Summary",
        "## Evidence",
        "## Rejected Alternatives",
        "## Runbook",
        "## Limitations / Runtime Truth",
        "## Glossary",
        "Audit seal",
    ]:
        assert section in source


def test_safety_runbooks_require_human_approval_and_no_auto_remediation() -> None:
    source = read_file("agent.py")
    assert '"human_approval_required": True' in source
    assert "No remediation was executed automatically." in source
    assert "human review" in source.lower()
