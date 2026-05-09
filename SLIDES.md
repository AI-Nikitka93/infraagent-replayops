# InfraAgent ReplayOps Slide Outline

## Slide 1 - Title
InfraAgent ReplayOps: Evidence-Verified Incident Triage on AMD

## Slide 2 - Problem
SRE teams are drowning in alert noise, tool sprawl, unclear ownership, and slow root-cause isolation. Dashboards show signals, but responders still need a packet that explains what happened, who owns it, and what to do safely.

## Slide 3 - Solution
InfraAgent ReplayOps converts an alert into an auditable War Room Packet:
- evidence timeline;
- root-cause citations;
- owner routing;
- business risk;
- safe runbook;
- runtime truth;
- deterministic eval score.

## Slide 4 - Architecture
Hugging Face Space -> Cloudflare Tunnel -> FastAPI polling API -> LangGraph -> local vLLM/Qwen on AMD MI300X -> mock observability fixtures.

## Slide 5 - Agent Workflow
Alert Ingestor -> Investigator -> Root Cause Analyst -> Runbook Generator -> Verification Gate.

## Slide 6 - AMD / Qwen
Qwen2.5-72B-Instruct runs through local vLLM on AMD Developer Cloud MI300X. Runtime proof distinguishes `live_vllm`, `runtime_unhealthy`, and `fallback_without_live_vllm`.

## Slide 7 - Demo Proof
Show READY status, scorecard, node trace, evidence IDs, business / ownership lens, and War Room Packet.

## Slide 8 - Why It Wins Track 1
It moves beyond simple RAG: it is a stateful incident workflow with typed tools, traceability, verification, and judge-visible proof.

## Slide 9 - Safety
No automatic remediation. Rollback, scaling, routing, and queue actions require human approval.

## Slide 10 - Next Steps
Replace mock observability fixtures with customer connectors, add persistent run store, and benchmark Qwen/vLLM latency across scenarios.
