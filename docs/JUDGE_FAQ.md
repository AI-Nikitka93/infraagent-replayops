# Judge FAQ

## What is live?

The FastAPI service, LangGraph workflow, polling API, Hugging Face Spaces UI, deterministic evaluator, evidence timeline, runbook generation, readiness gate, and War Room Packet are live code paths in this repository.

## What is mocked?

Metrics, logs, deploy events, traces, and topology are deterministic observability fixtures. They are mock data by design, so judges can replay the same incident and inspect whether the agent cited the expected evidence.

## What requires AMD proof?

Winning-tier AMD proof requires `runtime_proof.backend_mode=live_vllm`, a reachable vLLM `/v1/models` endpoint on AMD Developer Cloud MI300X, and `Qwen critic: ok` in the root-cause panel.

## Is this auto-remediation?

No. Recovery actions are human-approved recommendations. Rollback, scaling, queue mutation, routing changes, and runtime changes are not executed by the agent.

## Why is this not a generic dashboard?

A dashboard shows signals. InfraAgent ReplayOps turns an alert into a bounded agent workflow with evidence citations, rejected alternatives, ownership routing, deterministic scorecard, runtime truth, and an auditable packet.

## Why is this not simple RAG?

It does not retrieve documents to answer a question. It runs a stateful incident workflow with tool evidence, node trace, safety gates, and score-based verification.

## How should fallback be interpreted?

`fallback_without_live_vllm` means the product workflow works, but live Qwen critique is skipped. It must not be counted as AMD/Qwen proof.
