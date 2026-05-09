# Decisions

## 2026-05-09 - Graph Pattern
Decision: use a bounded sequential LangGraph pipeline with a verification gate, not a free-form supervisor that can route among many workers.

Reason: incident triage has a natural order: alert normalization, evidence collection, analysis, recovery plan, verification. A small deterministic graph is easier to demo in 1-2 minutes and easier to protect from loops while still showing agentic tool use.

Rejected: broad Supervisor + many workers | too much coordination overhead for a hackathon demo and higher risk of slow or confusing execution.

Directive: keep the graph at five nodes or fewer unless a real demo requirement proves that an extra node improves reliability.

## 2026-05-09 - External UI Contract
Decision: expose a polling API from FastAPI: `POST /api/triage` creates a run, `GET /api/status/{run_id}` returns current state and new events.

Reason: the P-18 infrastructure research found the public path should not rely on SSE or WebSocket through Cloudflare Quick Tunnel.

Rejected: streaming UI over SSE/WebSocket | not aligned with the selected tunnel constraint.

Directive: all UI progress must be recoverable from persisted run state and event cursor.

## 2026-05-09 - Tooling Scope
Decision: use deterministic mock observability tools for the demo instead of live Prometheus, Elasticsearch, tracing, or Kubernetes credentials.

Reason: the hackathon needs reliable evidence of an agentic workflow without depending on a real production cluster.

Rejected: live cluster dependencies | higher setup burden and lower demo reliability.

Directive: every mock tool must return structured evidence with IDs, timestamps, source names, and scenario identifiers.

## 2026-05-09 - Runtime Launch Surface
Decision: use root-level bash scripts for vLLM ROCm and Cloudflare Quick Tunnel instead of Docker Compose.

Reason: the P-18 report selected a `docker run` path with ROCm-specific device flags and explicit health checks. Bash keeps the hackathon launch path visible and easy to debug on the AMD VM.

Rejected: Docker Compose for vLLM | less direct control over startup checks and exact ROCm device mapping during the demo.

Directive: keep vLLM bound to `127.0.0.1:8000`; expose only the LangGraph/FastAPI API on `8010` through Cloudflare Tunnel.
