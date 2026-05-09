# InfraAgent ReplayOps Demo Script

Target length: 75-90 seconds.

## 0-10s - Open
"InfraAgent ReplayOps is an evidence-verified incident triage agent for the AMD Developer Hackathon. It turns a noisy production alert into an auditable War Room Packet."

Show: title, scenario selector, public Space URL.

## 10-25s - Start The Incident
Select `Checkout API deploy regression` and click `Start Evidence Triage`.

Say: "The UI is thin. It never calls Qwen, tools, or databases directly. It polls the FastAPI backend through the public tunnel."

## 25-45s - Show The Agent Workflow
Point to the node trace:
- alert ingestor
- investigator
- root cause analyst
- runbook generator
- verification gate

Say: "This is a bounded five-node LangGraph workflow. It is not an open-ended chat loop."

## 45-60s - Show Evidence And Business Lens
Point to evidence IDs, owner routing, business risk, and scorecard.

Say: "The agent correlates metrics, logs, deploy events, traces, and topology. The result is judge-verifiable because every root-cause claim cites stable evidence IDs."

## 60-75s - Show Runtime Truth
Point to Runtime proof.

Say: "The project does not fake AMD proof. If the backend reaches vLLM on the AMD MI300X VM, this panel shows `live_vllm` and Qwen critic output. If not, it says fallback and skips the critique."

## 75-90s - Close With The Packet
Open the War Room Packet.

Say: "The final artifact is the operational handoff: root cause, evidence, runbook, eval score, safety note, and audit seal."

## Required Recording Proof
The final video must visibly show:
- public HF Space URL;
- public API tunnel or app URL;
- runtime mode `live_vllm`;
- Qwen critic status `ok`;
- War Room Packet generated;
- `/api/readiness` with no formal blockers.
