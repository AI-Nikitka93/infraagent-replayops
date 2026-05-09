# Project Map

## Purpose
InfraAgent is a hackathon-grade incident triage system. It receives an alert, gathers mock observability evidence, explains the likely root cause, and generates a recovery runbook through a bounded LangGraph workflow.

## Scope
In scope:
- LangGraph state and node design.
- FastAPI polling contract for a Hugging Face Spaces UI.
- Mock tools for logs, metrics, deploy events, traces, topology, and runbook templates.
- vLLM/Qwen2.5-72B-Instruct as the local model endpoint behind the graph.

Out of scope for this architecture step:
- Executable graph code.
- Gradio UI code.
- Real production Prometheus, Elasticsearch, OpenTelemetry, or Kubernetes integrations.

## Runtime Topology
Browser -> Hugging Face Space UI -> HTTPS Cloudflare Tunnel -> FastAPI/LangGraph on AMD VM -> local vLLM -> Qwen2.5-72B-Instruct on MI300X.

## Key Documents
- Infrastructure research: `docs/research-report.md`
- Architecture: `docs/architecture.md`
- State graph: `docs/state_graph.md`
- Current state: `docs/STATE.md`
- Plan: `docs/EXEC_PLAN.md`
- Decisions: `docs/DECISIONS.md`

## Main Risks
- The public tunnel may add latency and instability, so the UI must poll and tolerate delayed status.
- Qwen2.5-72B inference can be slow if the vLLM parameters are too aggressive.
- Mock data must look credible enough to demonstrate agentic investigation rather than scripted text generation.
- The graph must avoid unbounded investigation loops.
