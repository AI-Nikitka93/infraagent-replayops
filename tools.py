from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from langchain_core.tools import tool


DEFAULT_SCENARIO = "checkout_deploy_regression"


PAIN_PROFILES: dict[str, dict[str, Any]] = {
    "deploy_regression": {
        "pain_profile": [
            "alert fatigue",
            "tool sprawl",
            "root cause uncertainty after deploys",
        ],
        "ownership_hint": "Route first to the checkout-api service owner and release manager.",
        "business_risk": "Revenue loss and reputational damage from failed checkout attempts.",
        "manual_triage_baseline_minutes": 25,
    },
    "downstream_dependency": {
        "pain_profile": [
            "tool sprawl",
            "unclear internal versus external ownership",
            "slow MTTR during dependency incidents",
        ],
        "ownership_hint": "Route first to payment-api owner, then vendor/provider escalation.",
        "business_risk": "Payment delay, cart abandonment, and support volume growth.",
        "manual_triage_baseline_minutes": 30,
    },
    "resource_leak": {
        "pain_profile": [
            "missed saturation signals",
            "knowledge silos",
            "restart loops without causal context",
        ],
        "ownership_hint": "Route first to inventory-api owner and platform runtime owner.",
        "business_risk": "False out-of-stock decisions and degraded product page conversion.",
        "manual_triage_baseline_minutes": 35,
    },
    "queue_backlog": {
        "pain_profile": [
            "alert fatigue",
            "unclear queue ownership",
            "delayed customer-visible workflows",
        ],
        "ownership_hint": "Route first to order-worker owner and fulfillment operations.",
        "business_risk": "Accepted orders become delayed or invisible to fulfillment systems.",
        "manual_triage_baseline_minutes": 28,
    },
    "inference_saturation": {
        "pain_profile": [
            "agentic observability",
            "AI workload performance blind spots",
            "token and queue saturation risk",
        ],
        "ownership_hint": "Route first to AI platform owner and AMD/vLLM runtime operator.",
        "business_risk": "Every Qwen-backed agent workflow slows when inference queues saturate.",
        "manual_triage_baseline_minutes": 22,
    },
}


SCENARIOS: dict[str, dict[str, Any]] = {
    "checkout_deploy_regression": {
        "label": "Checkout API deploy regression",
        "service": "checkout-api",
        "environment": "demo-prod",
        "incident_type": "deploy_regression",
        "business_impact": "Checkout failure blocks revenue-generating orders.",
        "expected_root_cause": "checkout-api release rc4 enabled a new order writer that caused orders-db lock waits and database timeouts.",
        "expected_evidence_ids": ["deploy.001", "metric.5xx.001", "metric.db_timeout.001", "log.timeout.001", "trace.db.001"],
        "expected_runbook_keywords": ["rollback", "new_order_writer", "5xx", "latency", "database timeout"],
        "metrics": [
            {
                "evidence_id": "metric.5xx.001",
                "metric": "http_5xx_rate",
                "baseline": "0.4%",
                "observed": "8.7%",
                "window": "10m",
                "severity_hint": "critical",
                "summary": "5xx rate rose sharply after checkout-api version 2026.05.09-rc4 was deployed.",
                "supports": "deploy_regression",
            },
            {
                "evidence_id": "metric.latency.001",
                "metric": "http_p95_latency_ms",
                "baseline": "280ms",
                "observed": "4200ms",
                "window": "10m",
                "severity_hint": "critical",
                "summary": "p95 latency increased 15x on checkout write requests.",
                "supports": "deploy_regression",
            },
            {
                "evidence_id": "metric.db_timeout.001",
                "metric": "db_timeout_rate",
                "baseline": "0.1%",
                "observed": "22.4%",
                "window": "10m",
                "severity_hint": "critical",
                "summary": "Database timeout rate tracks the checkout-api failure window.",
                "supports": "deploy_regression",
            },
        ],
        "logs": [
            {
                "evidence_id": "log.timeout.001",
                "timestamp": "2026-05-09T01:21:44+03:00",
                "level": "ERROR",
                "service": "checkout-api",
                "message": "POST /checkout failed: database lock wait timeout after 30000ms",
                "count_10m": 1842,
                "severity_hint": "critical",
                "supports": "deploy_regression",
            },
            {
                "evidence_id": "log.pool.001",
                "timestamp": "2026-05-09T01:22:03+03:00",
                "level": "WARN",
                "service": "checkout-api",
                "message": "db pool exhausted: active=128 idle=0 waiting=94",
                "count_10m": 611,
                "severity_hint": "warning",
                "supports": "deploy_regression",
            },
            {
                "evidence_id": "log.rollback_hint.001",
                "timestamp": "2026-05-09T01:23:11+03:00",
                "level": "INFO",
                "service": "checkout-api",
                "message": "feature flag new_order_writer=true for checkout-api rc4",
                "count_10m": 1,
                "severity_hint": "info",
                "supports": "deploy_regression",
            },
        ],
        "deploy_events": [
            {
                "evidence_id": "deploy.001",
                "timestamp": "2026-05-09T01:16:08+03:00",
                "service": "checkout-api",
                "version": "2026.05.09-rc4",
                "actor": "release-bot",
                "summary": "checkout-api deployed 5 minutes before the alert; enabled new_order_writer.",
                "severity_hint": "critical",
                "supports": "deploy_regression",
            }
        ],
        "traces": [
            {
                "evidence_id": "trace.db.001",
                "trace_group": "checkout-write-path",
                "slow_span": "orders-db.lock_wait",
                "p95_ms": 3680,
                "error_rate": "31%",
                "summary": "Most slow checkout traces spend time waiting on orders-db locks.",
                "severity_hint": "critical",
                "supports": "deploy_regression",
            }
        ],
        "topology": [
            {
                "evidence_id": "topology.checkout.001",
                "service": "checkout-api",
                "dependencies": ["orders-db", "payment-api", "inventory-api"],
                "blast_radius": ["checkout-web", "order-confirmation-worker"],
                "summary": "The failing service is on the revenue-critical checkout write path.",
                "severity_hint": "warning",
                "supports": "impact_assessment",
            }
        ],
    },
    "payments_dependency_slowdown": {
        "label": "Payment gateway dependency slowdown",
        "service": "payment-api",
        "environment": "demo-prod",
        "incident_type": "downstream_dependency",
        "business_impact": "Payment authorization slows down completed orders and raises cart abandonment risk.",
        "expected_root_cause": "external payment gateway latency dominated the payment-api authorize path.",
        "expected_evidence_ids": ["metric.payment.latency.001", "metric.provider.001", "log.gateway.001", "trace.gateway.001"],
        "expected_runbook_keywords": ["gateway", "degrade", "retry", "timeout", "provider"],
        "metrics": [
            {
                "evidence_id": "metric.payment.latency.001",
                "metric": "http_p95_latency_ms",
                "baseline": "310ms",
                "observed": "2900ms",
                "window": "15m",
                "severity_hint": "critical",
                "summary": "payment-api latency rose while CPU and memory stayed normal.",
                "supports": "downstream_dependency",
            },
            {
                "evidence_id": "metric.provider.001",
                "metric": "gateway_dependency_latency_ms",
                "baseline": "180ms",
                "observed": "2500ms",
                "window": "15m",
                "severity_hint": "critical",
                "summary": "External gateway latency dominates the payment request path.",
                "supports": "downstream_dependency",
            },
        ],
        "logs": [
            {
                "evidence_id": "log.gateway.001",
                "timestamp": "2026-05-09T01:27:30+03:00",
                "level": "WARN",
                "service": "payment-api",
                "message": "payment gateway request exceeded 2500ms threshold",
                "count_10m": 943,
                "severity_hint": "warning",
                "supports": "downstream_dependency",
            }
        ],
        "deploy_events": [],
        "traces": [
            {
                "evidence_id": "trace.gateway.001",
                "trace_group": "payment-authorize",
                "slow_span": "external-gateway.authorize",
                "p95_ms": 2510,
                "error_rate": "4%",
                "summary": "Slow span is outside payment-api, concentrated in gateway authorize calls.",
                "severity_hint": "critical",
                "supports": "downstream_dependency",
            }
        ],
        "topology": [
            {
                "evidence_id": "topology.payment.001",
                "service": "payment-api",
                "dependencies": ["external-gateway", "ledger-db", "fraud-api"],
                "blast_radius": ["checkout-api", "billing-worker"],
                "summary": "The latency path depends on an external payment gateway.",
                "severity_hint": "warning",
                "supports": "impact_assessment",
            }
        ],
    },
    "inventory_memory_leak": {
        "label": "Inventory API memory leak",
        "service": "inventory-api",
        "environment": "demo-prod",
        "incident_type": "resource_leak",
        "business_impact": "Inventory checks intermittently fail, causing false out-of-stock decisions.",
        "expected_root_cause": "inventory-api memory leak triggered container restarts and intermittent 500 responses.",
        "expected_evidence_ids": ["metric.mem.001", "metric.restart.001", "log.oom.001", "trace.inventory.001"],
        "expected_runbook_keywords": ["restart", "memory", "leak", "scale", "heap"],
        "metrics": [
            {
                "evidence_id": "metric.mem.001",
                "metric": "container_memory_working_set",
                "baseline": "42%",
                "observed": "96%",
                "window": "30m",
                "severity_hint": "critical",
                "summary": "Memory usage climbed steadily until the container hit the limit.",
                "supports": "resource_leak",
            },
            {
                "evidence_id": "metric.restart.001",
                "metric": "container_restart_count",
                "baseline": "0",
                "observed": "7",
                "window": "30m",
                "severity_hint": "critical",
                "summary": "Container restart count increased during the memory saturation window.",
                "supports": "resource_leak",
            },
        ],
        "logs": [
            {
                "evidence_id": "log.oom.001",
                "timestamp": "2026-05-09T01:33:08+03:00",
                "level": "ERROR",
                "service": "inventory-api",
                "message": "process killed after heap allocation failed near 1536MB limit",
                "count_10m": 21,
                "severity_hint": "critical",
                "supports": "resource_leak",
            }
        ],
        "deploy_events": [
            {
                "evidence_id": "deploy.inventory.001",
                "timestamp": "2026-05-09T00:52:41+03:00",
                "service": "inventory-api",
                "version": "2026.05.09-cache-prewarm",
                "actor": "release-bot",
                "summary": "Inventory cache prewarm release shipped 40 minutes before memory saturation.",
                "severity_hint": "warning",
                "supports": "resource_leak",
            }
        ],
        "traces": [
            {
                "evidence_id": "trace.inventory.001",
                "trace_group": "inventory-lookup",
                "slow_span": "inventory-api.cache_hydrate",
                "p95_ms": 1800,
                "error_rate": "12%",
                "summary": "Slow traces cluster around cache hydration before process restarts.",
                "severity_hint": "warning",
                "supports": "resource_leak",
            }
        ],
        "topology": [
            {
                "evidence_id": "topology.inventory.001",
                "service": "inventory-api",
                "dependencies": ["catalog-db", "redis-cache"],
                "blast_radius": ["checkout-api", "product-page"],
                "summary": "Inventory API is queried by checkout and product detail pages.",
                "severity_hint": "warning",
                "supports": "impact_assessment",
            }
        ],
    },
    "queue_backlog_worker_stall": {
        "label": "Order worker queue backlog",
        "service": "order-worker",
        "environment": "demo-prod",
        "incident_type": "queue_backlog",
        "business_impact": "Orders are accepted but confirmation emails and fulfillment events are delayed.",
        "expected_root_cause": "order-worker consumer lag grew after workers stalled on a poison message batch.",
        "expected_evidence_ids": ["metric.queue.001", "metric.worker.001", "log.poison.001", "trace.queue.001"],
        "expected_runbook_keywords": ["queue", "poison", "dead-letter", "consumer", "backlog"],
        "metrics": [
            {
                "evidence_id": "metric.queue.001",
                "metric": "queue_visible_messages",
                "baseline": "120",
                "observed": "18400",
                "window": "20m",
                "severity_hint": "critical",
                "summary": "Order queue visible messages grew more than 150x.",
                "supports": "queue_backlog",
            },
            {
                "evidence_id": "metric.worker.001",
                "metric": "worker_success_rate",
                "baseline": "99.5%",
                "observed": "41%",
                "window": "20m",
                "severity_hint": "critical",
                "summary": "Worker success rate dropped while queue backlog grew.",
                "supports": "queue_backlog",
            },
        ],
        "logs": [
            {
                "evidence_id": "log.poison.001",
                "timestamp": "2026-05-09T01:39:10+03:00",
                "level": "ERROR",
                "service": "order-worker",
                "message": "message batch repeatedly failed validation: schema_version=2024-legacy",
                "count_10m": 302,
                "severity_hint": "critical",
                "supports": "queue_backlog",
            }
        ],
        "deploy_events": [],
        "traces": [
            {
                "evidence_id": "trace.queue.001",
                "trace_group": "order-worker-consume",
                "slow_span": "queue.receive_batch",
                "p95_ms": 1220,
                "error_rate": "48%",
                "summary": "Worker trace shows repeated validation failures on the same message cohort.",
                "severity_hint": "critical",
                "supports": "queue_backlog",
            }
        ],
        "topology": [
            {
                "evidence_id": "topology.worker.001",
                "service": "order-worker",
                "dependencies": ["orders-queue", "email-provider", "fulfillment-api"],
                "blast_radius": ["customer-email", "warehouse-events"],
                "summary": "Worker backlog affects customer communication and fulfillment handoff.",
                "severity_hint": "warning",
                "supports": "impact_assessment",
            }
        ],
    },
    "vllm_saturation": {
        "label": "vLLM inference saturation",
        "service": "qwen-vllm",
        "environment": "amd-mi300x-demo",
        "incident_type": "inference_saturation",
        "business_impact": "Agent workflows slow down because model requests queue behind long-context prompts.",
        "expected_root_cause": "vLLM queueing increased after long-context requests consumed scheduler and KV cache capacity.",
        "expected_evidence_ids": ["metric.vllm.queue.001", "metric.vllm.latency.001", "log.vllm.001", "trace.vllm.001"],
        "expected_runbook_keywords": ["vllm", "queue", "max_model_len", "concurrency", "kv cache"],
        "metrics": [
            {
                "evidence_id": "metric.vllm.queue.001",
                "metric": "vllm_waiting_requests",
                "baseline": "0-2",
                "observed": "37",
                "window": "5m",
                "severity_hint": "critical",
                "summary": "vLLM waiting request queue rose during long-context traffic.",
                "supports": "inference_saturation",
            },
            {
                "evidence_id": "metric.vllm.latency.001",
                "metric": "time_to_first_token_ms",
                "baseline": "900ms",
                "observed": "9400ms",
                "window": "5m",
                "severity_hint": "critical",
                "summary": "Time to first token increased more than 10x.",
                "supports": "inference_saturation",
            },
        ],
        "logs": [
            {
                "evidence_id": "log.vllm.001",
                "timestamp": "2026-05-09T01:43:18+03:00",
                "level": "WARN",
                "service": "qwen-vllm",
                "message": "scheduler queue depth high; long prefill requests dominate active batch",
                "count_10m": 88,
                "severity_hint": "warning",
                "supports": "inference_saturation",
            }
        ],
        "deploy_events": [
            {
                "evidence_id": "deploy.vllm.001",
                "timestamp": "2026-05-09T01:34:00+03:00",
                "service": "qwen-vllm",
                "version": "qwen2.5-72b-32768ctx",
                "actor": "demo-operator",
                "summary": "Context length increased to 32768 before load simulation.",
                "severity_hint": "warning",
                "supports": "inference_saturation",
            }
        ],
        "traces": [
            {
                "evidence_id": "trace.vllm.001",
                "trace_group": "agent-llm-call",
                "slow_span": "vllm.prefill",
                "p95_ms": 8100,
                "error_rate": "0%",
                "summary": "Slow spans cluster in vLLM prefill rather than tool execution.",
                "severity_hint": "critical",
                "supports": "inference_saturation",
            }
        ],
        "topology": [
            {
                "evidence_id": "topology.vllm.001",
                "service": "qwen-vllm",
                "dependencies": ["amd-mi300x", "rocm", "cloudflare-tunnel", "langgraph-api"],
                "blast_radius": ["all-agent-workflows"],
                "summary": "Inference saturation affects every LangGraph node that calls Qwen.",
                "severity_hint": "critical",
                "supports": "impact_assessment",
            }
        ],
    },
}


def available_scenarios() -> list[dict[str, str]]:
    return [
        {
            "scenario_id": scenario_id,
            "label": scenario["label"],
            "service": scenario["service"],
            "incident_type": scenario["incident_type"],
        }
        for scenario_id, scenario in SCENARIOS.items()
    ]


def scenario_metadata(scenario_id: str | None) -> dict[str, Any]:
    scenario = _scenario_payload(scenario_id)
    pain = PAIN_PROFILES.get(scenario["incident_type"], PAIN_PROFILES["deploy_regression"])
    return {
        "scenario_id": scenario_id or DEFAULT_SCENARIO,
        "label": scenario["label"],
        "service": scenario["service"],
        "environment": scenario["environment"],
        "incident_type": scenario["incident_type"],
        "business_impact": scenario["business_impact"],
        "pain_profile": pain["pain_profile"],
        "ownership_hint": pain["ownership_hint"],
        "business_risk": pain["business_risk"],
        "manual_triage_baseline_minutes": pain["manual_triage_baseline_minutes"],
        "expected_root_cause": scenario["expected_root_cause"],
        "expected_evidence_ids": scenario["expected_evidence_ids"],
        "expected_runbook_keywords": scenario["expected_runbook_keywords"],
    }


def _scenario_payload(scenario_id: str | None) -> dict[str, Any]:
    key = scenario_id or DEFAULT_SCENARIO
    return deepcopy(SCENARIOS.get(key, SCENARIOS[DEFAULT_SCENARIO]))


def _json_response(source: str, scenario_id: str | None, evidence: list[dict[str, Any]]) -> str:
    payload = {
        "source": source,
        "scenario_id": scenario_id or DEFAULT_SCENARIO,
        "evidence": evidence,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _tag_records(source: str, scenario_id: str, service: str, window_minutes: int, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence = []
    for item in records:
        record = deepcopy(item)
        record["source"] = source
        record["scenario_id"] = scenario_id
        record["requested_service"] = service
        record["window_minutes"] = window_minutes
        evidence.append(record)
    return evidence


@tool
def get_metric_anomaly(service: str, scenario_id: str = DEFAULT_SCENARIO, window_minutes: int = 20) -> str:
    """Return realistic mock metric anomalies for an incident investigation."""
    scenario = _scenario_payload(scenario_id)
    evidence = _tag_records("get_metric_anomaly", scenario_id, service, window_minutes, scenario["metrics"])
    return _json_response("get_metric_anomaly", scenario_id, evidence)


@tool
def get_recent_logs(service: str, scenario_id: str = DEFAULT_SCENARIO, window_minutes: int = 20) -> str:
    """Return realistic mock log patterns around an incident window."""
    scenario = _scenario_payload(scenario_id)
    evidence = _tag_records("get_recent_logs", scenario_id, service, window_minutes, scenario["logs"])
    return _json_response("get_recent_logs", scenario_id, evidence)


@tool
def get_deploy_events(service: str, scenario_id: str = DEFAULT_SCENARIO, window_minutes: int = 60) -> str:
    """Return mock deploy and config events near an incident."""
    scenario = _scenario_payload(scenario_id)
    evidence = _tag_records("get_deploy_events", scenario_id, service, window_minutes, scenario["deploy_events"])
    return _json_response("get_deploy_events", scenario_id, evidence)


@tool
def get_trace_spans(service: str, scenario_id: str = DEFAULT_SCENARIO, window_minutes: int = 20) -> str:
    """Return mock trace span summaries showing slow dependencies."""
    scenario = _scenario_payload(scenario_id)
    evidence = _tag_records("get_trace_spans", scenario_id, service, window_minutes, scenario["traces"])
    return _json_response("get_trace_spans", scenario_id, evidence)


@tool
def get_service_topology(service: str, scenario_id: str = DEFAULT_SCENARIO, window_minutes: int = 20) -> str:
    """Return mock service topology and blast-radius evidence."""
    scenario = _scenario_payload(scenario_id)
    evidence = _tag_records("get_service_topology", scenario_id, service, window_minutes, scenario["topology"])
    return _json_response("get_service_topology", scenario_id, evidence)


OBSERVABILITY_TOOLS = [
    get_metric_anomaly,
    get_recent_logs,
    get_deploy_events,
    get_trace_spans,
    get_service_topology,
]


def collect_mock_evidence(service: str, scenario_id: str, window_minutes: int = 20) -> dict[str, Any]:
    metric_payload = json.loads(get_metric_anomaly.invoke({
        "service": service,
        "scenario_id": scenario_id,
        "window_minutes": window_minutes,
    }))
    log_payload = json.loads(get_recent_logs.invoke({
        "service": service,
        "scenario_id": scenario_id,
        "window_minutes": window_minutes,
    }))
    deploy_payload = json.loads(get_deploy_events.invoke({
        "service": service,
        "scenario_id": scenario_id,
        "window_minutes": 60,
    }))
    trace_payload = json.loads(get_trace_spans.invoke({
        "service": service,
        "scenario_id": scenario_id,
        "window_minutes": window_minutes,
    }))
    topology_payload = json.loads(get_service_topology.invoke({
        "service": service,
        "scenario_id": scenario_id,
        "window_minutes": window_minutes,
    }))

    grouped = {
        "metrics": metric_payload["evidence"],
        "logs": log_payload["evidence"],
        "deploy_events": deploy_payload["evidence"],
        "traces": trace_payload["evidence"],
        "topology": topology_payload["evidence"],
        "tool_errors": [],
    }
    grouped["items"] = flatten_evidence(grouped)
    return grouped


def flatten_evidence(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in ["metrics", "logs", "deploy_events", "traces", "topology"]:
        for record in evidence.get(group, []):
            item = deepcopy(record)
            item["group"] = group
            items.append(item)
    return items


def evaluate_triage(
    scenario_id: str,
    root_cause: dict[str, Any] | None,
    runbook: dict[str, Any] | None,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    metadata = scenario_metadata(scenario_id)
    collected_ids = {item.get("evidence_id") for item in flatten_evidence(evidence)}
    expected_ids = set(metadata["expected_evidence_ids"])
    cited_ids = set((root_cause or {}).get("supporting_evidence_ids") or [])
    cited_expected = expected_ids.intersection(cited_ids)
    collected_expected = expected_ids.intersection(collected_ids)

    root_text = json.dumps(root_cause or {}, ensure_ascii=False).lower()
    expected_root_words = {word.strip(".,:;()").lower() for word in metadata["expected_root_cause"].split() if len(word) > 5}
    matched_root_words = [word for word in expected_root_words if word in root_text]

    runbook_text = json.dumps(runbook or {}, ensure_ascii=False).lower()
    expected_keywords = metadata["expected_runbook_keywords"]
    matched_keywords = [keyword for keyword in expected_keywords if keyword.lower() in runbook_text]

    evidence_coverage = len(collected_expected) / max(len(expected_ids), 1)
    citation_coverage = len(cited_expected) / max(len(expected_ids), 1)
    root_match = min(len(matched_root_words) / max(min(len(expected_root_words), 8), 1), 1.0)
    runbook_completeness = len(matched_keywords) / max(len(expected_keywords), 1)
    total = round((evidence_coverage * 30) + (citation_coverage * 30) + (root_match * 20) + (runbook_completeness * 20))

    return {
        "scenario_id": scenario_id,
        "score": total,
        "max_score": 100,
        "grade": "pass" if total >= 75 else "review",
        "checks": {
            "expected_evidence_collected": sorted(collected_expected),
            "expected_evidence_missing": sorted(expected_ids - collected_ids),
            "expected_evidence_cited": sorted(cited_expected),
            "root_cause_keyword_match": round(root_match, 2),
            "runbook_keyword_match": matched_keywords,
            "evidence_coverage": round(evidence_coverage, 2),
            "citation_coverage": round(citation_coverage, 2),
            "runbook_completeness": round(runbook_completeness, 2),
        },
        "verdict": (
            "The run produced enough evidence, cited the expected signals, and generated an actionable runbook."
            if total >= 75
            else "The run needs review because expected evidence, citations, or runbook actions were incomplete."
        ),
    }
