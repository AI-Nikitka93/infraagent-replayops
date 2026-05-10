from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Iterable

import gradio as gr
import requests


API_BASE_ENV = "INFRAAGENT_API_BASE"
API_KEY_ENV = "INFRAAGENT_API_KEY"
REQUEST_TIMEOUT_SECONDS = 15
POLL_INTERVAL_SECONDS = float(os.getenv("INFRAAGENT_POLL_INTERVAL_SECONDS", "2"))
MAX_POLL_ATTEMPTS = int(os.getenv("INFRAAGENT_MAX_POLL_ATTEMPTS", "60"))
TERMINAL_STATUSES = {"ready", "failed", "needs_human_review"}

SCENARIOS: dict[str, dict[str, str]] = {
    "checkout_deploy_regression": {
        "label": "Checkout API deploy regression",
        "service": "checkout-api",
        "environment": "demo-prod",
        "severity": "critical",
        "title": "High 5xx rate and latency spike",
        "description": "5xx rate and checkout latency spiked shortly after a release.",
    },
    "payments_dependency_slowdown": {
        "label": "Payment gateway dependency slowdown",
        "service": "payment-api",
        "environment": "demo-prod",
        "severity": "major",
        "title": "Payment authorization latency spike",
        "description": "Payment authorization latency rose while service CPU and memory stayed normal.",
    },
    "inventory_memory_leak": {
        "label": "Inventory API memory leak",
        "service": "inventory-api",
        "environment": "demo-prod",
        "severity": "major",
        "title": "Inventory API restart loop",
        "description": "Inventory lookups fail after memory climbs and containers restart.",
    },
    "queue_backlog_worker_stall": {
        "label": "Order worker queue backlog",
        "service": "order-worker",
        "environment": "demo-prod",
        "severity": "major",
        "title": "Order queue backlog is growing",
        "description": "Order confirmations are delayed while worker success rate falls.",
    },
    "vllm_saturation": {
        "label": "vLLM inference saturation",
        "service": "qwen-vllm",
        "environment": "amd-mi300x-demo",
        "severity": "major",
        "title": "Agent inference latency spike",
        "description": "Agent graph slows down after long-context model requests saturate vLLM.",
    },
    "insufficient_evidence_unknown_outage": {
        "label": "Unknown outage with insufficient evidence",
        "service": "edge-router",
        "environment": "demo-prod",
        "severity": "major",
        "title": "Intermittent customer errors with weak telemetry",
        "description": "Only a partial edge metric and broad topology are available, so the agent must refuse a premature root cause.",
    },
}

DEFAULT_ALERT = (
    "PagerDuty alert: checkout-api is serving elevated 5xx responses and p95 latency is above 4s. "
    "The incident began a few minutes after the latest deployment."
)

CSS = """
.gradio-container { max-width: 1280px !important; }
.ops-shell {
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 18px 20px;
  background: #f8fafc;
}
.ops-shell h1 { margin: 0 0 8px 0; font-size: 26px; line-height: 1.2; }
.muted { color: #475569; }
.ops-command {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}
.ops-kpi {
  border: 1px solid #dbe3ee;
  border-radius: 8px;
  padding: 10px 12px;
  background: #ffffff;
  min-height: 82px;
}
.ops-kpi strong { display: block; color: #0f172a; margin-bottom: 4px; }
.icon-system {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 22px;
  height: 22px;
  border: 1px solid #94a3b8;
  border-radius: 6px;
  margin-right: 6px;
  color: #0f172a;
  font-size: 13px;
}
.panel-tight textarea, .panel-tight .wrap { font-size: 13px; }
.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 6px 12px;
  font-weight: 700;
  border: 1px solid #cbd5e1;
}
.status-running, .status-queued {
  color: #854d0e;
  background: #fef3c7;
  border-color: #f59e0b;
}
.status-ready {
  color: #14532d;
  background: #dcfce7;
  border-color: #22c55e;
}
.status-failed, .status-error {
  color: #7f1d1d;
  background: #fee2e2;
  border-color: #ef4444;
}
.status-review {
  color: #3730a3;
  background: #e0e7ff;
  border-color: #6366f1;
}
.status-idle {
  color: #334155;
  background: #f1f5f9;
  border-color: #cbd5e1;
}
@media (max-width: 760px) {
  .ops-shell { padding: 16px; }
  .ops-command { grid-template-columns: 1fr; }
}
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def api_base() -> str:
    return os.getenv(API_BASE_ENV, "").strip().rstrip("/")


def api_key() -> str:
    return os.getenv(API_KEY_ENV, "").strip()


def auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key()}",
        "Content-Type": "application/json",
    }


def status_badge(status_value: str, node: str | None = None, run_id: str | None = None) -> str:
    normalized = (status_value or "idle").lower()
    css_class = {
        "ready": "status-ready",
        "running": "status-running",
        "queued": "status-queued",
        "failed": "status-failed",
        "needs_human_review": "status-review",
        "error": "status-error",
        "idle": "status-idle",
    }.get(normalized, "status-idle")
    node_text = node or "not started"
    run_text = f"<span class='muted'>Run: {run_id}</span>" if run_id else "<span class='muted'>No active run</span>"
    return (
        f"<div><span class='status-pill {css_class}'>{normalized.upper()}</span> "
        f"<span class='muted'>Node: <strong>{node_text}</strong></span><br>{run_text}</div>"
    )


def compact_json(value: Any) -> str:
    return json.dumps(value or {}, ensure_ascii=False, indent=2)


def format_runtime(proof: dict[str, Any] | None) -> str:
    if not proof:
        return "Runtime proof will appear after the alert is ingested."
    healthy = proof.get("healthy")
    mode = proof.get("backend_mode", "unknown")
    lines = [
        f"**Observed backend:** `{mode}`",
        f"**Model:** `{proof.get('model', 'unknown')}`",
        f"**Target AMD stack:** {proof.get('target_hardware', 'AMD MI300X')} with {proof.get('runtime_stack', 'unknown')}",
        f"**Observed hardware:** {proof.get('observed_hardware', 'not verified')}",
        f"**Health:** `{healthy}`",
        f"**Latency:** `{proof.get('latency_ms', 'n/a')} ms`",
        f"**Truth contract:** {proof.get('runtime_truth', 'No runtime truth note returned.')}",
    ]
    models = proof.get("available_models") or []
    if models:
        lines.append(f"**Served models:** {', '.join(f'`{item}`' for item in models)}")
    if proof.get("error"):
        lines.append(f"**Runtime note:** {proof['error']}")
    return "\n\n".join(lines)


def format_business_case(case: dict[str, Any] | None) -> str:
    if not case:
        return "Business / ownership lens appears after verification."
    lines = [
        "**Pain profile:** " + ", ".join(f"`{item}`" for item in case.get("pain_profile", [])),
        f"**Owner routing:** {case.get('ownership_hint', 'unknown')}",
        f"**Business risk:** {case.get('business_risk', 'unknown')}",
        f"**Manual triage baseline:** `{case.get('manual_triage_baseline_minutes', 'n/a')} minutes`",
        f"**Observed graph duration:** `{case.get('observed_graph_duration_seconds', 'n/a')} seconds`",
        "",
        "**Judge value:**",
    ]
    lines.extend([f"- {item}" for item in case.get("judge_value", [])])
    lines.append("")
    lines.append("**Market alignment:**")
    lines.extend([f"- {item}" for item in case.get("market_alignment", [])])
    return "\n".join(lines)


def format_readiness(readiness: dict[str, Any] | None) -> str:
    if not readiness:
        return "Submission Readiness will appear after the backend returns a readiness report."
    blockers = readiness.get("formal_blockers") or []
    local_package = readiness.get("local_package", {})
    external = readiness.get("external_submission", {})
    lines = [
        f"**Verdict:** `{readiness.get('verdict', 'unknown')}`",
        f"**Local package:** `{local_package.get('passed', 0)}/{local_package.get('total', 0)}`",
        f"**External submission:** `{external.get('passed', 0)}/{external.get('total', 0)}`",
        readiness.get("truth_note", ""),
        "",
        "**Open blockers:**",
    ]
    lines.extend([f"- `{item}`" for item in blockers] or ["- none"])
    return "\n".join(lines)


def format_degraded_state(status_payload: dict[str, Any] | None) -> str:
    if not status_payload:
        return "Degraded State will show Qwen, tunnel, run, evidence, and readiness blockers after polling starts."
    runtime = status_payload.get("runtime_proof") or {}
    readiness = status_payload.get("submission_readiness") or {}
    scorecard = status_payload.get("eval_scorecard") or {}
    status_value = status_payload.get("status", "unknown")
    blockers = readiness.get("formal_blockers") or []
    evidence_missing = (scorecard.get("checks") or {}).get("expected_evidence_missing") or []
    notes = [
        f"**Run state:** `{status_value}`",
        f"**Qwen/vLLM:** `{runtime.get('backend_mode', 'not checked')}`",
        f"**Tunnel/API:** `reachable` once this panel is polling; failed requests render as network errors.",
        f"**Evidence gate:** `{scorecard.get('grade', 'pending')}`",
        "**Readiness blockers:** " + (", ".join(f"`{item}`" for item in blockers) if blockers else "none returned"),
    ]
    if runtime.get("backend_mode") != "live_vllm":
        notes.append("**No live Qwen:** graph remains usable, but the Qwen critic is skipped and runtime truth stays degraded.")
    if status_value == "needs_human_review" or evidence_missing:
        missing = ", ".join(f"`{item}`" for item in evidence_missing) if evidence_missing else "evidence did not pass the automated gate"
        notes.append(f"**Evidence insufficient:** {missing}. Human review remains required.")
    return "\n\n".join(notes)


def format_glossary() -> str:
    return "\n".join([
        "- **Evidence ID:** stable citation key for each metric, log, deploy event, trace, or topology record.",
        "- **Runtime proof:** backend health, model identity, latency, and AMD/vLLM truth captured by the API.",
        "- **Scorecard:** deterministic checks for evidence coverage, citation coverage, root-cause fit, and runbook completeness.",
        "- **Owner/Risk:** practical handoff target and business consequence for the incident commander.",
        "- **Packet:** final War Room Packet with audit seal, rejected alternatives, limitations, and safety notes.",
    ])


def format_scorecard(scorecard: dict[str, Any] | None) -> str:
    if not scorecard:
        return "Evaluation scorecard will appear after verification."
    checks = scorecard.get("checks", {})
    lines = [
        f"### Score: {scorecard.get('score')}/{scorecard.get('max_score')}",
        f"**Grade:** `{scorecard.get('grade')}`",
        scorecard.get("verdict", ""),
        "",
        "**Evidence collected:** " + ", ".join(f"`{item}`" for item in checks.get("expected_evidence_collected", [])),
        "**Evidence cited:** " + ", ".join(f"`{item}`" for item in checks.get("expected_evidence_cited", [])),
        f"**Citation coverage:** `{checks.get('citation_coverage', 0)}`",
        f"**Runbook completeness:** `{checks.get('runbook_completeness', 0)}`",
    ]
    missing = checks.get("expected_evidence_missing") or []
    if missing:
        lines.append("**Missing expected evidence:** " + ", ".join(f"`{item}`" for item in missing))
    return "\n\n".join(lines)


def format_trace(traces: list[dict[str, Any]] | None) -> str:
    if not traces:
        return "Agent trace will appear as LangGraph nodes complete."
    lines = []
    for item in traces[-10:]:
        tools = ", ".join(f"`{tool}`" for tool in item.get("tool_calls", [])) or "no tools"
        observations = "; ".join(item.get("observations", []))
        lines.append(
            f"- **{item.get('node')}** `{item.get('status')}` "
            f"({item.get('duration_ms')} ms): {item.get('decision')}  \n"
            f"  Tools: {tools}. Observations: {observations}"
        )
    return "\n".join(lines)


def format_evidence(items: list[dict[str, Any]] | None) -> str:
    if not items:
        return "Evidence timeline will appear after the Investigator calls mock observability tools."
    lines = []
    for item in items:
        severity = item.get("severity_hint", "info").upper()
        group = item.get("group", item.get("source", "evidence"))
        summary = item.get("summary") or item.get("message") or "No summary."
        lines.append(f"- `{item.get('evidence_id')}` **{severity}** [{group}] {summary}")
    return "\n".join(lines)


def format_root_cause(root_cause: dict[str, Any] | None) -> str:
    if not root_cause:
        return "Root cause will appear after the analyst node has enough evidence."
    evidence = root_cause.get("supporting_evidence_ids") or []
    critic = root_cause.get("qwen_critic") or {}
    lines = [
        f"### {root_cause.get('confidence', 'unknown').upper()} confidence",
        root_cause.get("summary", "No summary returned."),
        "",
        "**Supporting evidence:**",
    ]
    lines.extend([f"- `{item}`" for item in evidence] or ["- No evidence IDs returned."])
    rejected = root_cause.get("rejected_causes") or []
    if rejected:
        lines.append("")
        lines.append("**Rejected alternatives:**")
        for item in rejected:
            lines.append(f"- {item.get('summary', 'Unknown cause')}: {item.get('reason', 'No reason returned.')}")
    lines.append("")
    lines.append("**Qwen critic:**")
    if critic.get("status") == "ok":
        lines.append(critic.get("content", "No critic text returned."))
    else:
        lines.append(f"`{critic.get('status', 'pending')}` - {critic.get('reason') or critic.get('error') or 'No live critique yet.'}")
    return "\n".join(lines)


def list_section(title: str, values: Iterable[str]) -> list[str]:
    items = list(values)
    if not items:
        return [f"**{title}:**", "- Not returned."]
    return [f"**{title}:**", *[f"- {item}" for item in items]]


def format_runbook(runbook: dict[str, Any] | None) -> str:
    if not runbook:
        return "Runbook will appear after the recovery planning node completes."
    lines = [
        f"### {runbook.get('title', 'Recovery runbook')}",
        runbook.get("root_cause_summary", ""),
        "",
        *list_section("Immediate actions", runbook.get("immediate_actions") or []),
        "",
        *list_section("Validation steps", runbook.get("validation_steps") or []),
        "",
        *list_section("Rollback / reversal plan", runbook.get("rollback_plan") or []),
        "",
        f"**Human approval required:** `{runbook.get('human_approval_required', True)}`",
    ]
    risks = runbook.get("risk_notes") or []
    if risks:
        lines.append("")
        lines.extend(list_section("Risk notes", risks))
    return "\n".join(lines)


def format_events(status_payload: dict[str, Any], existing_log: list[str]) -> list[str]:
    events = status_payload.get("new_events") or []
    for event in events:
        seq = event.get("seq", "?")
        node = event.get("node", "unknown")
        message = event.get("message", "")
        existing_log.append(f"`#{seq}` **{node}** - {message}")
    return existing_log[-20:]


def output_tuple(
    status_html: str,
    node_md: str,
    runtime_md: str,
    scorecard_md: str,
    business_md: str,
    readiness_md: str,
    degraded_md: str,
    glossary_md: str,
    trace_md: str,
    evidence_md: str,
    root_md: str,
    runbook_md: str,
    packet: str,
    incident_json: Any,
    events_md: str,
) -> tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, Any, str]:
    return (
        status_html,
        node_md,
        runtime_md,
        scorecard_md,
        business_md,
        readiness_md,
        degraded_md,
        glossary_md,
        trace_md,
        evidence_md,
        root_md,
        runbook_md,
        packet,
        incident_json,
        events_md,
    )


def config_error() -> tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, Any, str]:
    message = "Missing HF Space secrets. Set `INFRAAGENT_API_BASE` and `INFRAAGENT_API_KEY`."
    return output_tuple(
        status_badge("error", "configuration"),
        message,
        "Runtime proof unavailable because the backend URL or API key is not configured.",
        "Evaluation unavailable.",
        "Business lens unavailable.",
        "Submission readiness unavailable.",
        "Degraded State: missing `INFRAAGENT_API_BASE` or `INFRAAGENT_API_KEY`.",
        format_glossary(),
        "Trace unavailable.",
        "Evidence unavailable.",
        "Root cause unavailable.",
        "Runbook unavailable.",
        "War Room Packet unavailable.",
        {},
        message,
    )


def request_error(message: str, run_id: str | None = None) -> tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, Any, str]:
    return output_tuple(
        status_badge("error", "network", run_id),
        f"Network or API error: {message}",
        "Runtime proof unavailable because the request failed.",
        "Evaluation unavailable.",
        "Business lens unavailable.",
        "Submission readiness unavailable.",
        "Degraded State: public API request failed; verify tunnel URL, backend process, and bearer token.",
        format_glossary(),
        "Trace unavailable.",
        "Evidence unavailable.",
        "Root cause unavailable.",
        "Runbook unavailable.",
        "War Room Packet unavailable.",
        {"run_id": run_id},
        f"Request failed at {utc_now()}.",
    )


def build_payload(alert_text: str, scenario_id: str) -> dict[str, Any]:
    scenario = SCENARIOS.get(scenario_id, SCENARIOS["checkout_deploy_regression"])
    clean_alert = alert_text.strip() or DEFAULT_ALERT
    return {
        "alert_id": f"ui-{int(time.time())}",
        "service": scenario["service"],
        "environment": scenario["environment"],
        "severity": scenario["severity"],
        "title": scenario["title"],
        "description": f"{scenario['description']}\n\nOperator alert: {clean_alert}",
        "started_at": utc_now(),
        "scenario_id": scenario_id,
        "alert_payload": clean_alert,
    }


def post_triage(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{api_base()}/api/triage",
        headers=auth_headers(),
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def get_status(run_id: str, cursor: int | None = None) -> dict[str, Any]:
    params = {"cursor": cursor} if cursor is not None else None
    response = requests.get(
        f"{api_base()}/api/status/{run_id}",
        headers=auth_headers(),
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def format_node(status_payload: dict[str, Any]) -> str:
    progress = status_payload.get("progress") or {}
    completed = progress.get("completed_nodes") or []
    current_node = status_payload.get("current_node") or "waiting"
    step_count = progress.get("step_count", 0)
    max_steps = progress.get("max_steps", 7)
    completed_text = ", ".join(f"`{item}`" for item in completed) if completed else "none yet"
    return (
        f"**Current node:** `{current_node}`\n\n"
        f"**Step budget:** `{step_count}/{max_steps}`\n\n"
        f"**Completed nodes:** {completed_text}"
    )


def run_triage(alert_text: str, scenario_id: str):
    if not api_base() or not api_key():
        yield config_error()
        return

    payload = build_payload(alert_text, scenario_id)
    event_log: list[str] = []

    try:
        start_payload = post_triage(payload)
    except requests.RequestException as exc:
        yield request_error(str(exc))
        return

    run_id = start_payload.get("run_id")
    if not run_id:
        yield request_error(f"Backend did not return run_id: {compact_json(start_payload)}")
        return

    yield output_tuple(
        status_badge(start_payload.get("status", "queued"), "queued", run_id),
        "**Current node:** `queued`\n\nWaiting for the graph to start.",
        "Runtime proof pending. The alert ingestor probes the vLLM endpoint first.",
        "Evaluation pending.",
        "Business lens pending.",
        "Submission readiness pending.",
        "Degraded State pending.",
        format_glossary(),
        "Trace pending.",
        "Evidence pending.",
        "Root cause pending.",
        "Runbook pending.",
        "War Room Packet pending.",
        {"alert": payload, "run_id": run_id},
        f"`#0` **api** - Run created at {utc_now()}.",
    )

    final_payload: dict[str, Any] | None = None
    cursor: int | None = None
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL_SECONDS)
        try:
            status_payload = get_status(run_id, cursor=cursor)
        except requests.RequestException as exc:
            yield request_error(str(exc), run_id)
            return

        event_log = format_events(status_payload, event_log)
        cursor = status_payload.get("next_cursor", cursor)
        final_payload = status_payload
        status_value = status_payload.get("status", "unknown")
        current_node = status_payload.get("current_node") or "waiting"
        yield output_tuple(
            status_badge(status_value, current_node, run_id),
            format_node(status_payload),
            format_runtime(status_payload.get("runtime_proof")),
            format_scorecard(status_payload.get("eval_scorecard")),
            format_business_case(status_payload.get("business_case")),
            format_readiness(status_payload.get("submission_readiness")),
            format_degraded_state(status_payload),
            format_glossary(),
            format_trace(status_payload.get("node_traces")),
            format_evidence(status_payload.get("evidence_items")),
            format_root_cause(status_payload.get("root_cause")),
            format_runbook(status_payload.get("runbook")),
            status_payload.get("war_room_packet") or "War Room Packet will appear after verification.",
            status_payload.get("incident_context") or {"run_id": run_id, "status": status_value},
            "\n".join(event_log) or f"`poll {attempt}` Waiting for graph events.",
        )

        if status_value in TERMINAL_STATUSES:
            return

    timeout_note = (
        f"Polling stopped after {MAX_POLL_ATTEMPTS} attempts "
        f"({int(MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS)} seconds)."
    )
    yield output_tuple(
        status_badge("error", "poll_timeout", run_id),
        timeout_note,
        format_runtime(final_payload.get("runtime_proof") if final_payload else None),
        format_scorecard(final_payload.get("eval_scorecard") if final_payload else None),
        format_business_case(final_payload.get("business_case") if final_payload else None),
        format_readiness(final_payload.get("submission_readiness") if final_payload else None),
        format_degraded_state(final_payload),
        format_glossary(),
        format_trace(final_payload.get("node_traces") if final_payload else None),
        format_evidence(final_payload.get("evidence_items") if final_payload else None),
        format_root_cause(final_payload.get("root_cause") if final_payload else None),
        format_runbook(final_payload.get("runbook") if final_payload else None),
        final_payload.get("war_room_packet", "War Room Packet unavailable.") if final_payload else "War Room Packet unavailable.",
        final_payload.get("incident_context", {"run_id": run_id}) if final_payload else {"run_id": run_id},
        "\n".join([*event_log, timeout_note]),
    )


def build_app() -> gr.Blocks:
    scenario_choices = [(value["label"], key) for key, value in SCENARIOS.items()]
    with gr.Blocks(title="InfraAgent ReplayOps") as demo:
        gr.HTML(
            """
            <section class="ops-shell">
              <h1>InfraAgent ReplayOps: Evidence-Verified Incident Triage</h1>
              <p class="muted">
                Thin Hugging Face Spaces command surface for an incident agent: what happened, what the graph does, which evidence it cites, and whether AMD/Qwen runtime proof is live.
              </p>
              <div class="ops-command">
                <div class="ops-kpi"><strong><span class="icon-system">!</span>Status</strong><span class="muted">Incident state, active node, and run ID.</span></div>
                <div class="ops-kpi"><strong><span class="icon-system">E</span>Evidence</strong><span class="muted">Stable IDs cited in root cause and packet.</span></div>
                <div class="ops-kpi"><strong><span class="icon-system">A</span>AMD proof</strong><span class="muted">vLLM health, model ID, latency, runtime truth.</span></div>
                <div class="ops-kpi"><strong><span class="icon-system">P</span>Packet</strong><span class="muted">War Room Packet with score and audit seal.</span></div>
              </div>
            </section>
            """
        )

        with gr.Row():
            with gr.Column(scale=4):
                scenario = gr.Dropdown(
                    choices=scenario_choices,
                    value="checkout_deploy_regression",
                    label="Incident replay scenario",
                    info="Each scenario has expected evidence IDs, expected root cause, and evaluator checks.",
                )
                alert_text = gr.Textbox(
                    value=DEFAULT_ALERT,
                    label="Incoming alert",
                    lines=5,
                    max_lines=8,
                    info="The UI sends this alert to the backend. It never calls tools, databases, or the model directly.",
                )
                start = gr.Button("Start Evidence Triage", variant="primary")
            with gr.Column(scale=3):
                status_output = gr.HTML(value=status_badge("idle"))
                node_output = gr.Markdown("**Current node:** `not started`")
                runtime_output = gr.Markdown("Runtime proof will appear after the first backend poll.")

        with gr.Row():
            scorecard_output = gr.Markdown(label="Eval Scorecard", value="Evaluation scorecard will appear after verification.")
            business_output = gr.Markdown(label="Business / Ownership Lens", value="Business / Ownership Lens will appear after verification.")
            readiness_output = gr.Markdown(label="Submission Readiness", value="Submission Readiness gate will appear after backend verification.")
            degraded_output = gr.Markdown(label="Degraded State", value="Degraded State will show runtime, tunnel, run, evidence, and readiness blockers.")

        with gr.Row():
            glossary_output = gr.Markdown(label="Proof Glossary", value=format_glossary())
            trace_output = gr.Markdown(label="Live Agent Trace", value="Agent trace will appear as nodes complete.")

        with gr.Row():
            evidence_output = gr.Markdown(label="Evidence Timeline", value="Evidence timeline will appear after tool calls.")
            incident_output = gr.JSON(label="Incident Context")

        with gr.Row():
            root_output = gr.Markdown(label="Root Cause", value="Root cause will appear after analysis.")
            runbook_output = gr.Markdown(label="Runbook", value="Runbook will appear after recovery planning.")

        with gr.Row():
            packet_output = gr.Textbox(
                label="War Room Packet",
                value="War Room Packet will appear after verification.",
                lines=16,
                max_lines=24,
                buttons=["copy"],
            )
            events_output = gr.Markdown(label="Graph Events", value="No run started.")

        start.click(
            fn=run_triage,
            inputs=[alert_text, scenario],
            outputs=[
                status_output,
                node_output,
                runtime_output,
                scorecard_output,
                business_output,
                readiness_output,
                degraded_output,
                glossary_output,
                trace_output,
                evidence_output,
                root_output,
                runbook_output,
                packet_output,
                incident_output,
                events_output,
            ],
            show_progress="full",
            concurrency_limit=2,
        )
    return demo


demo = build_app()


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=2).launch(css=CSS)
