# Competition Review - AMD Developer Hackathon

Checked on: 2026-05-09 Europe/Minsk  
Source focus: official Lablab AMD Developer Hackathon page and visible Lablab submission pages/search results.

## Verdict

The current InfraAgent implementation is a useful technical scaffold, but it is not prize-ready.

It currently demonstrates a bounded LangGraph incident workflow with mock observability tools, a polling FastAPI API, and a Hugging Face Spaces UI. That is enough for a working demo, but not enough for a serious shot at Grand Prize or Track Prize because the field already contains projects with stronger proof, sharper positioning, and more visible AMD/Qwen technical depth.

## Official Competition Signals

Source: https://lablab.ai/ai-hackathons/amd-developer

Confirmed signals:
- Track 1 asks teams to move beyond simple RAG and build sophisticated AI agentic systems and workloads.
- The page explicitly says submissions should feel real, work end-to-end, and show what AMD's compute stack unlocks.
- Track 1 stack examples include LangChain, CrewAI, AutoGen, and open-source models such as Qwen.
- AMD Developer Cloud and ROCm are not background details. They are part of the scoring story.
- Build-in-public and meaningful AMD/ROCm feedback are extra signals.

Implication:
- A thin incident assistant with only deterministic mock data looks underpowered unless it visibly proves runtime value, benchmark value, agent traceability, or operational value.

## Competitive Field Observed

### ROCm AgentOps

Source: https://lablab.ai/ai-hackathons/amd-developer/rocm-agentops/rocm-agentops

Observed positioning:
- Operational assurance layer for AI agents on AMD-backed inference infrastructure.
- Ingests business incidents, AMD/vLLM workload signals, endpoint health checks, benchmark evidence, and optional ROCm/GPU telemetry.
- Includes trust/confidence scoring, routing, policy guardrails, audit seals, War Room Packet export, and benchmark proof.
- Claims a validated AMD/vLLM run with Qwen/Qwen2.5-7B-Instruct and 20/20 successful benchmark requests.

Why this matters:
- This is close to our current InfraAgent space, but it has a stronger evidence/audit/benchmark story.
- It makes the AMD/vLLM layer visible to judges instead of hiding it behind an incident UI.

### AegisOps AI

Source: https://lablab.ai/ai-hackathons/amd-developer/ztothez/aegisops-ai

Observed positioning:
- Multi-agent security workflow that converts MITRE ATT&CK inputs into defensive readiness packages.
- Agents generate threat scenarios, observables, Sigma-style detections, mitigation guidance, and validation.
- Runs on AMD Developer Cloud infrastructure and emphasizes operational SOC value.

Why this matters:
- It is not generic "incident triage"; it produces domain-specific artifacts that a SOC team recognizes.
- It has clearer buyer value than a generic runbook assistant.

### ROCmPort AI

Source: https://lablab.ai/ai-hackathons/amd-developer/compute-catalyst/rocmport-ai-agentic-migration-suite

Observed positioning:
- Agentic CUDA-to-ROCm migration suite.
- Scans repository AST, drafts diff patches, generates Dockerfile and runbook.
- Claims AMD Developer Cloud proof and 67.7 tokens/sec Qwen throughput on MI300X.

Why this matters:
- Very sponsor-aligned: it directly solves ROCm adoption friction.
- It turns AMD from "inference host" into the actual reason the product exists.

### ROCmPilot

Source: https://lablab.ai/ai-hackathons/amd-developer/atomai/rocmpilot

Observed positioning:
- Agentic developer tool for CUDA/NVIDIA-first workloads moving toward AMD ROCm.
- Audits Dockerfiles, Python inference code, vLLM scripts, dependencies, health checks, and benchmark scripts.
- Separates estimates from live AMD proof.

Why this matters:
- Same sponsor-alignment pattern: migration/readiness/proof around AMD is stronger than generic infra assistant.

### AppBid

Source: https://lablab.ai/ai-hackathons/amd-developer/appbid/appbid

Observed positioning:
- Finance reverse-auction marketplace using lender agents.
- Uses Qwen 72B serving on AMD MI300X, lender-specific policy profiles, live bid streams, and GPU telemetry.

Why this matters:
- It has clearer business value and a live workflow that non-technical judges can understand.
- It uses Qwen 72B and MI300X as part of the product narrative, not just as backend infrastructure.

## Current InfraAgent Weaknesses

Evidence from current workspace:
- Backend and UI exist, but mock observability data drives the core demo.
- The current UI shows incident status, root cause, and runbook, but not a strong evidence trail, benchmark panel, GPU runtime proof, or eval score.
- The graph is clean and bounded, but the product story is a familiar SRE triage assistant.
- AMD MI300X/vLLM/Qwen are configured in scripts, but not yet visible as a judged technical achievement.

Competitive risk:
- "AI incident triage" is crowded inside this contest.
- A generic alert -> logs -> root cause -> runbook flow can look like a polished wrapper unless we show real agentic evidence, runtime telemetry, and measurable evaluation.

## Recommended Pivot

Do not throw away the current code. Reposition and deepen it.

New positioning:

**InfraAgent ReplayOps: Evidence-Verified Incident Triage on AMD ROCm**

One-line pitch:
InfraAgent ReplayOps turns infrastructure incidents into replayable, evidence-backed triage packets by combining LangGraph agents, Qwen on AMD MI300X/vLLM, synthetic-but-realistic telemetry, runtime proof, and a judge-visible evaluation scoreboard.

What changes:
- The demo is no longer "an AI writes a runbook."
- The demo becomes "an AI investigation produces an auditable incident packet with evidence IDs, tool calls, confidence, runtime telemetry, and pass/fail evals."

Why this is stronger:
- It directly answers "sophisticated agentic workflow."
- It gives judges visible proof of tool use and verification.
- It makes AMD/vLLM/Qwen performance part of the UI.
- It creates a defensible wedge against AegisOps/ROCm AgentOps: replayable incident evaluation and evidence scoring, not broad SOC/AgentOps platform claims.

## Required Upgrade Scope

### 1. Evidence Graph

Add every tool result as a first-class evidence item:
- `evidence_id`
- `source`
- `timestamp`
- `scenario_id`
- `finding`
- `confidence`
- `used_by_node`

UI must show an "Evidence Timeline" and not just final text.

### 2. Agent Trace Panel

Expose the LangGraph progression:
- current node
- node start/end time
- tool calls
- observations collected
- decision made

This lets judges see the agentic workflow rather than infer it.

### 3. Runtime Proof Panel

Show AMD/Qwen/vLLM facts collected from the running environment:
- model id
- vLLM base URL health
- request latency
- tokens/sec if available
- backend mode: live vLLM or fallback mock
- ROCm/MI300X telemetry if available

If live telemetry is unavailable, label it as unavailable instead of faking it.

### 4. Incident Replay Evaluation

Create 5 deterministic scenarios:
- DB lock causing payment latency
- memory leak causing API 500s
- queue backlog causing delayed jobs
- cache outage causing elevated DB reads
- model server saturation causing inference latency

Each scenario needs:
- expected root cause
- expected evidence IDs
- expected runbook actions
- pass/fail evaluator

UI should show an Eval Scorecard:
- root cause match
- evidence coverage
- runbook completeness
- time to diagnosis

### 5. War Room Packet Export

Generate a compact markdown/JSON packet:
- incident summary
- evidence list
- root cause
- remediation plan
- confidence and limitations
- runtime proof
- run_id hash

This creates a submission artifact judges can inspect.

## What Not To Do

- Do not keep polishing the current UI as if visual polish alone fixes competitiveness.
- Do not broaden into a full AegisOps clone.
- Do not claim "production-ready" if the run still depends on only hardcoded mock evidence.
- Do not hide the AMD/Qwen layer in scripts; judges need to see it in the product.
- Do not add more agents for show. Add proof, evaluation, and traceability.

## Next Build Plan

1. Update backend state schema to include evidence items, node traces, runtime proof, and eval results.
2. Expand mock tools into scenario-backed evidence providers.
3. Add an evaluator node or deterministic post-run evaluator.
4. Extend `/api/status/{run_id}` to return trace, evidence, runtime proof, and scorecard.
5. Redesign Gradio UI into an Incident Commander dashboard with:
   - Live Graph Progress
   - Evidence Timeline
   - Runtime Proof
   - Root Cause
   - Runbook
   - Eval Scorecard
   - War Room Packet
6. Run a local contract test proving the UI does not call localhost and polls the backend only.

## Go / No-Go

Go only if we can implement evidence-first ReplayOps in the remaining time.

No-go for prize ambitions if the project remains a simple mock incident triage demo.

