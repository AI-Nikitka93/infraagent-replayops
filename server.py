from __future__ import annotations

import asyncio
import json
import os
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field


load_dotenv()

HOST = os.getenv("LANGGRAPH_HOST", "127.0.0.1")
PORT = int(os.getenv("LANGGRAPH_PORT", "8010"))

app = FastAPI(
    title="InfraAgent API",
    version="0.1.0",
    description="Polling API for LangGraph incident triage.",
)
security = HTTPBearer(auto_error=False)
RUNS: dict[str, dict[str, Any]] = {}
RUN_LOCK = asyncio.Lock()
ROOT = Path(__file__).resolve().parent
CONTEST_TRUTH_FILE = ROOT / "docs" / "contest_truth.json"
AGENT_RUNTIME: dict[str, Any] | None = None


class TriageRequest(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"alert-{uuid.uuid4().hex[:8]}")
    alert_payload: str | None = None
    service: str = "checkout-api"
    environment: str = "demo-prod"
    severity: str = "critical"
    title: str = "High 5xx rate and latency spike"
    description: str = "Synthetic incident for InfraAgent demo."
    started_at: str | None = None
    scenario_id: str = "checkout_deploy_regression"


class TriageAccepted(BaseModel):
    run_id: str
    status: str
    status_url: str
    poll_after_ms: int
    created_at: str


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load_contest_truth() -> dict[str, Any]:
    if not CONTEST_TRUTH_FILE.is_file():
        return {
            "checked_at": None,
            "selected_track": "unknown",
            "judge_gap_statement": "contest truth snapshot missing",
            "freshness_sensitive_dependencies": [],
        }
    return json.loads(CONTEST_TRUTH_FILE.read_text(encoding="utf-8"))


def load_agent_runtime() -> dict[str, Any]:
    global AGENT_RUNTIME
    if AGENT_RUNTIME is None:
        import agent

        AGENT_RUNTIME = {
            "create_initial_state": agent.create_initial_state,
            "stream_triage": agent.stream_triage,
        }
    return AGENT_RUNTIME


async def require_api_key(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> None:
    public_api_key = validate_public_api_key()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be: Bearer <PUBLIC_API_KEY>",
        )
    if credentials.credentials != public_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid PUBLIC_API_KEY.",
        )


def validate_public_api_key() -> str:
    value = os.getenv("PUBLIC_API_KEY", "").strip()
    if not value or value.startswith("CHANGE_ME"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PUBLIC_API_KEY is not configured. Set a generated secret before exposing the API.",
        )
    return value


def public_state(state: dict[str, Any], cursor: int | None = None) -> dict[str, Any]:
    events = state.get("ui_events", [])
    if cursor is not None:
        events = [event for event in events if int(event.get("seq", 0)) > cursor]
    next_cursor = max([int(event.get("seq", 0)) for event in state.get("ui_events", [])] or [0])
    control = state.get("control", {})
    response = {
        "run_id": state["run_id"],
        "status": state.get("status", "unknown"),
        "current_node": state.get("current_node"),
        "progress": {
            "completed_nodes": list(control.get("node_visits", {}).keys()),
            "active_node": None if state.get("status") in {"ready", "failed", "needs_human_review"} else state.get("current_node"),
            "step_count": control.get("step_count", 0),
            "max_steps": control.get("max_steps", 7),
        },
        "new_events": events,
        "next_cursor": next_cursor,
        "poll_after_ms": 0 if state.get("status") in {"ready", "failed", "needs_human_review"} else 1500,
        "incident_context": state.get("incident_context"),
        "evidence_items": state.get("evidence_items", []),
        "node_traces": state.get("node_traces", []),
        "runtime_proof": state.get("runtime_proof", {}),
        "business_case": state.get("business_case", {}),
        "submission_readiness": build_submission_readiness(state.get("runtime_proof", {}), state.get("root_cause")),
        "root_cause": state.get("root_cause"),
        "runbook": state.get("runbook"),
        "eval_scorecard": state.get("eval_scorecard"),
        "war_room_packet": state.get("war_room_packet"),
        "audit": {
            "trace_id": state.get("audit", {}).get("trace_id"),
            "model": state.get("audit", {}).get("model"),
            "tool_call_count": len(state.get("audit", {}).get("tool_calls", [])),
            "updated_at": state.get("audit", {}).get("updated_at"),
        },
    }
    if state.get("status") in {"ready", "needs_human_review", "failed"}:
        response["errors"] = state.get("errors", [])
    return response


def build_submission_readiness(runtime_proof: dict[str, Any] | None = None, root_cause: dict[str, Any] | None = None) -> dict[str, Any]:
    runtime_proof = runtime_proof or {}
    root_cause = root_cause or {}
    qwen_critic = root_cause.get("qwen_critic") or {}
    amd_runtime_evidence = runtime_proof.get("amd_runtime_evidence") or {}
    contest_truth = load_contest_truth()
    file_checks = {
        "license": (ROOT / "LICENSE").is_file(),
        "readme": (ROOT / "README.md").is_file(),
        "submission_copy": (ROOT / "SUBMISSION.md").is_file(),
        "demo_script": (ROOT / "DEMO_SCRIPT.md").is_file(),
        "slide_outline": (ROOT / "SLIDES.md").is_file(),
        "market_pain_map": (ROOT / "docs" / "market-pain-map.md").is_file(),
        "public_repo_gitignore": (ROOT / ".gitignore").is_file(),
    }
    external_checks = {
        "live_vllm": runtime_proof.get("backend_mode") == "live_vllm",
        "amd_runtime_proof": amd_runtime_evidence.get("ok") is True,
        "qwen_critic_ok": qwen_critic.get("status") == "ok",
        "hf_space_url": bool(os.getenv("HF_SPACE_URL", "").strip()),
        "public_repo_url": bool(os.getenv("PUBLIC_REPO_URL", "").strip()),
        "demo_video_url": bool(os.getenv("DEMO_VIDEO_URL", "").strip()),
        "slide_deck_url": bool(os.getenv("SLIDE_DECK_URL", "").strip()),
    }
    formal_blockers = [
        name
        for name, passed in {**file_checks, **external_checks}.items()
        if not passed
    ]
    local_passed = sum(1 for passed in file_checks.values() if passed)
    external_passed = sum(1 for passed in external_checks.values() if passed)
    return {
        "contest_truth": {
            "checked_at": contest_truth.get("checked_at"),
            "selected_track": contest_truth.get("selected_track"),
            "judge_gap_statement": contest_truth.get("judge_gap_statement"),
            "freshness_sensitive_dependencies": contest_truth.get("freshness_sensitive_dependencies", []),
        },
        "local_package": {
            "passed": local_passed,
            "total": len(file_checks),
            "checks": file_checks,
        },
        "external_submission": {
            "passed": external_passed,
            "total": len(external_checks),
            "checks": external_checks,
        },
        "formal_blockers": formal_blockers,
        "verdict": "GO" if not formal_blockers else "NO_GO_UNTIL_BLOCKERS_CLOSE",
        "truth_note": "Readiness is strict: fallback demo proof does not count as live AMD/Qwen proof.",
        "live_proof_requirements": [
            "AMD MI300X runtime device proof exists on the target VM.",
            "vLLM /v1/models returns the served Qwen model from the AMD VM.",
            "A public run returns runtime_proof.backend_mode=live_vllm.",
            "The root cause panel returns Qwen critic: ok.",
            "The public status payload returns runtime_proof.amd_runtime_evidence.ok=true.",
            "War Room Packet and readiness evidence are captured with timestamp.",
        ],
    }


async def save_run_state(run_id: str, state: dict[str, Any]) -> None:
    async with RUN_LOCK:
        RUNS[run_id] = deepcopy(state)


async def execute_triage(run_id: str, alert: dict[str, Any]) -> None:
    runtime = load_agent_runtime()
    state = runtime["create_initial_state"](run_id, alert)
    state["status"] = "running"
    await save_run_state(run_id, state)
    try:
        async for update in runtime["stream_triage"](state, run_id):
            await save_run_state(run_id, update)
    except Exception as exc:
        failed_state = deepcopy(RUNS.get(run_id, state))
        failed_state["status"] = "failed"
        failed_state["current_node"] = "runtime"
        failed_state.setdefault("errors", []).append({
            "source": "execute_triage",
            "error": str(exc),
            "created_at": now_iso(),
        })
        failed_state.setdefault("ui_events", []).append({
            "seq": len(failed_state.get("ui_events", [])) + 1,
            "node": "runtime",
            "type": "run_failed",
            "message": "Triage run failed during graph execution.",
            "payload": {"error": str(exc)},
            "created_at": now_iso(),
        })
        await save_run_state(run_id, failed_state)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "infraagent-api"}


@app.get("/api/readiness")
async def submission_readiness() -> dict[str, Any]:
    return build_submission_readiness()


@app.post("/api/triage", response_model=TriageAccepted, dependencies=[Depends(require_api_key)])
async def start_triage(request: TriageRequest) -> TriageAccepted:
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    created_at = now_iso()
    runtime = load_agent_runtime()
    initial_state = runtime["create_initial_state"](run_id, request.model_dump())
    await save_run_state(run_id, initial_state)
    asyncio.create_task(execute_triage(run_id, request.model_dump()))
    return TriageAccepted(
        run_id=run_id,
        status="queued",
        status_url=f"/api/status/{run_id}",
        poll_after_ms=1500,
        created_at=created_at,
    )


@app.get("/api/status/{run_id}", dependencies=[Depends(require_api_key)])
async def get_status(run_id: str, cursor: int | None = None) -> dict[str, Any]:
    async with RUN_LOCK:
        state = deepcopy(RUNS.get(run_id))
    if state is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="run_id not found")
    return public_state(state, cursor=cursor)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8010, reload=False)
