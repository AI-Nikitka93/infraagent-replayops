from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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


def test_backend_surfaces_market_pain_and_ownership_lens() -> None:
    tools_source = read_file("tools.py")
    agent_source = read_file("agent.py")
    for text in ["pain_profile", "ownership_hint", "business_risk", "manual_triage_baseline_minutes"]:
        assert text in tools_source
        assert text in agent_source
