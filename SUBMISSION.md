# InfraAgent ReplayOps - AMD Developer Hackathon Submission Draft

Current judge-facing gap statement: fallback demo verified, live AMD/Qwen proof pending.

## Project Title
InfraAgent ReplayOps

## Short Description
Evidence-verified incident triage on AMD: a LangGraph agent turns noisy alerts into auditable War Room Packets with evidence IDs, owner routing, runtime truth, and human-approved recovery plans.

## Long Description
InfraAgent ReplayOps targets the daily pain of SRE and platform teams: too many alerts, too little context, unclear ownership, and slow root-cause isolation. The demo receives an incident alert from a Hugging Face Spaces UI, sends it to a FastAPI polling API, and runs a bounded five-node LangGraph workflow:

1. Alert Ingestor normalizes the incident and probes the local vLLM endpoint.
2. Investigator calls deterministic mock observability tools for metrics, logs, deploy events, traces, and topology.
3. Root Cause Analyst ranks causes with evidence citations and asks Qwen for a strict critique when `live_vllm` is available.
4. Runbook Generator produces safe, human-approved recovery steps.
5. Verification Gate scores the run and exports a War Room Packet with an audit seal.

The project is intentionally not a simple RAG demo. It shows agent state, tool evidence, node traces, citation coverage, business risk, ownership routing, and a deterministic evaluation scorecard.

## AMD / Qwen Usage
Target runtime is AMD MI300X on AMD Developer Cloud with ROCm and local vLLM serving `Qwen/Qwen2.5-72B-Instruct` through an OpenAI-compatible API. The backend exposes a runtime truth contract:

- `live_vllm`: `/v1/models` answered from the configured vLLM endpoint and Qwen critique can run.
- `runtime_unhealthy`: vLLM answered but failed health checks.
- `fallback_without_live_vllm`: graph, UI, evidence, scorecard, and packet work, but Qwen critique is skipped.

Current local Windows proof may show `fallback_without_live_vllm`. Final AMD submission proof must show `live_vllm`.

## What Is Mocked
The production observability sources are represented by deterministic mock observability fixtures. They are not presented as live Prometheus, Elasticsearch, tracing, or Kubernetes data. The mock design is deliberate: it makes the hackathon demo stable and lets judges inspect whether the agent cited the expected evidence.

## Technology Tags
AMD Developer Cloud, AMD ROCm, MI300X, vLLM, Qwen2.5-72B-Instruct, LangGraph, FastAPI, Hugging Face Spaces, Gradio, Cloudflare Tunnel, agentic observability, SRE, incident response.

## Demo Path For Judges
1. Open the Hugging Face Space.
2. Select `Checkout API deploy regression`.
3. Click `Start Evidence Triage`.
4. Watch the node trace: Alert -> Evidence -> Cause -> Runbook -> Eval.
5. Confirm runtime proof. Winning submission proof should show `live_vllm`.
6. Inspect evidence timeline, business / ownership lens, root cause citations, runbook, and War Room Packet.
7. Open `/api/readiness` on the public API URL to verify remaining submission blockers.

## Not A Generic Incident Assistant

InfraAgent ReplayOps is not a chat layer over alerts and not a passive dashboard. It runs a bounded agent workflow that produces a replayable incident packet with evidence IDs, rejected alternatives, owner routing, deterministic score, runtime truth, and human-approved recovery steps.

## Why AMD Matters

The target proof is local Qwen2.5-72B-Instruct served by vLLM on AMD Developer Cloud MI300X with ROCm. The AMD path matters because the model critique runs beside the agent service and can be verified through the runtime proof panel. The submission is not considered live-AMD complete until the public run shows `live_vllm` and `Qwen critic: ok`.

## Judge FAQ

See `docs/JUDGE_FAQ.md`.

- What is live: API, LangGraph workflow, UI, evaluator, packet generation.
- What is mocked: deterministic observability fixtures.
- What is human-approved: every recovery action.
- What is not auto-remediation: rollback, scaling, routing, and queue mutation are not executed.

## Build in Public Technical Walkthrough

See `docs/BUILD_IN_PUBLIC.md` for two technical update posts and honest notes on ROCm, AMD Developer Cloud, vLLM/Qwen, Hugging Face Spaces, and Cloudflare Tunnel friction.

## Contingency Wording

If the final AMD runtime fails before deadline: "The public ReplayOps workflow is verified in fallback mode, but the winning-tier AMD proof is not complete because the public run does not show `live_vllm` and `Qwen critic: ok`."

## Honest Limitations
- The demo does not execute remediation.
- Destructive actions require human approval.
- Observability inputs are deterministic mock fixtures.
- Qwen contributes only when `runtime_proof.backend_mode=live_vllm`.
- Public GitHub, HF Space, video, slide, and API URLs are listed below; refresh the API URL if the tunnel changes.

## Artifacts to refresh after live AMD proof
- README, SUBMISSION, HACKATHON_READINESS, STATE, state.json, EXEC_PLAN, and PROJECT_HISTORY.
- Final demo video, slide deck, screenshot, `.runtime/amd_live_proof.json`, and `.runtime/public_demo_status.json`.
- HF Space secrets and public API URL if the AMD-backed tunnel changes.

## Stable Public Access Plan
- Preferred judging path: named Cloudflare Tunnel on a stable hostname targeting FastAPI on port `8010`.
- Fallback judging path: refreshed Quick Tunnel through `scripts/refresh_public_demo.py` immediately before judging.
- Safety boundary: expose only the agent API, never raw vLLM on port `8000`.

## Public Links
- Public GitHub Repository: https://github.com/AI-Nikitka93/infraagent-replayops
- Hugging Face Space: https://huggingface.co/spaces/clendeningantonettie/infraagent-replayops
- Demo Application URL: https://clendeningantonettie-infraagent-replayops.hf.space
- Public API Tunnel: https://seattle-rock-south-bath.trycloudflare.com
- Video Presentation: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-demo.mp4
- Slide Presentation: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-slides.pdf

## Final Proof Still Required
The public package is ready for submission review, but the winning-tier proof is still incomplete until the AMD Developer Cloud run visibly shows `runtime_proof.backend_mode=live_vllm` and `Qwen critic: ok`.

Latest public fallback smoke: Hugging Face Space reached `READY`, `Score: 100/100`, evidence timeline, runtime truth, and War Room Packet after refreshing `INFRAAGENT_API_BASE` to the current Cloudflare Tunnel. This proves the public demo path works, but it still does not count as live AMD/Qwen proof.

## Final Submit Gate

Before final submission, run:

```bash
python scripts/final_submission_gate.py --api-base "$INFRAAGENT_API_BASE" --api-key-file .runtime/local_api_key.txt --space-host https://clendeningantonettie-infraagent-replayops.hf.space
```

Submit only if the verdict is `GO_SUBMIT`. The gate blocks on missing AMD device proof, missing `live_vllm`, missing `Qwen critic: ok`, failed public smoke, failed audits, or `/api/readiness` not returning `GO`.
