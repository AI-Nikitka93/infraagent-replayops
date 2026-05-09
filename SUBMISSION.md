# InfraAgent ReplayOps - AMD Developer Hackathon Submission Draft

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

## Honest Limitations
- The demo does not execute remediation.
- Destructive actions require human approval.
- Observability inputs are deterministic mock fixtures.
- Qwen contributes only when `runtime_proof.backend_mode=live_vllm`.
- Public GitHub, HF Space, video, and slide URLs must be inserted before final submission.

## Links To Fill Before Final Submission
- Public GitHub Repository: https://github.com/AI-Nikitka93/infraagent-replayops
- Hugging Face Space: https://huggingface.co/spaces/clendeningantonettie/infraagent-replayops
- Demo Application URL: https://clendeningantonettie-infraagent-replayops.hf.space
- Public API Tunnel: https://seattle-rock-south-bath.trycloudflare.com
- Video Presentation: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-demo.mp4
- Slide Presentation: https://github.com/AI-Nikitka93/infraagent-replayops/raw/main/submission_assets/infraagent-replayops-slides.pdf

## Final Proof Still Required
The public package is ready for submission review, but the winning-tier proof is still incomplete until the AMD Developer Cloud run visibly shows `runtime_proof.backend_mode=live_vllm` and `Qwen critic: ok`.

Latest public fallback smoke: Hugging Face Space reached `READY`, `Score: 100/100`, evidence timeline, runtime truth, and War Room Packet after refreshing `INFRAAGENT_API_BASE` to the current Cloudflare Tunnel. This proves the public demo path works, but it still does not count as live AMD/Qwen proof.
