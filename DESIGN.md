---
version: alpha
name: InfraAgent ReplayOps
description: Evidence-first incident command UI for an AMD Developer Hackathon LangGraph triage agent.
colors:
  canvas: "#F8FAFC"
  surface: "#FFFFFF"
  surfaceMuted: "#EEF2F7"
  ink: "#0F172A"
  textMuted: "#475569"
  border: "#CBD5E1"
  evidence: "#2563EB"
  runtime: "#0F766E"
  risk: "#B91C1C"
  warning: "#A16207"
  success: "#15803D"
typography:
  h1:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: 760
    lineHeight: 1.2
    letterSpacing: 0
  h2:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0
  body:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1.45
    letterSpacing: 0
rounded:
  sm: 6px
  md: 8px
spacing:
  xs: 6px
  sm: 10px
  md: 16px
  lg: 24px
components:
  ops-shell:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: 18px
  ops-kpi:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: 12px
  status-pill:
    backgroundColor: "{colors.surfaceMuted}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: 8px
  evidence-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
    padding: 10px
---

## Overview

InfraAgent ReplayOps is an operational war-room surface, not a marketing landing page. The UI must show what happened, what the agent is doing, which evidence supports the result, and whether the AMD/Qwen runtime proof is live. The first viewport must expose status, score, live runtime, root cause, and packet readiness within ten seconds.

The direction is evidence-first and calm: dense but readable, restrained color, no decorative gradients, no oversized hero copy, no fictional production data, and no visual borrowing from external brands.

## Colors

Use neutral operational surfaces with semantic accents only when the accent carries state or evidence meaning.

- Evidence blue marks cited signals, timeline items, and evidence IDs.
- Runtime teal marks vLLM, Qwen, AMD, and API health.
- Risk red marks customer impact, failed runs, unsafe actions, and readiness blockers.
- Warning amber marks degraded state, weak evidence, human review, and skipped Qwen critique.
- Success green marks verified readiness or passing evaluator gates.

## Typography

Use compact incident-command typography. The main title can be 26px; panels, scorecards, and runbook sections stay 14-18px. Monospace is reserved for evidence IDs, run IDs, model IDs, API paths, audit seals, and status values.

## Layout

The command shell has four first-viewport KPIs: Status, Evidence, AMD proof, and Packet. Below it, keep panels in this order: run controls, runtime proof, eval scorecard, business/ownership lens, submission readiness, degraded state, proof glossary, agent trace, evidence timeline, root cause, runbook, War Room Packet, graph events.

Responsive behavior must collapse KPI and panel rows to one column below 760px. Do not let long evidence IDs or audit seals overflow; wrap monospace text and keep panel padding stable.

## Components

- `ops-shell`: first-viewport command band with product name and the four operational KPIs.
- `ops-kpi`: fixed-density summary tile with a compact icon, label, and one-line purpose.
- `status-pill`: visible state label for queued, running, ready, failed, needs human review, and error.
- `evidence-row`: timeline row with evidence ID, severity, source group, and summary.
- `runtime-proof`: markdown panel with backend mode, model, target AMD stack, observed hardware, health, latency, and truth contract.
- `scorecard`: non-decorative evaluator panel with score, grade, evidence collected, evidence cited, citation coverage, and missing evidence.
- `degraded-state`: explicit panel for no live Qwen, tunnel down/API failure, run failed, evidence insufficient, and readiness blocker.
- `war-room-packet`: copyable text artifact containing summary, evidence, rejected alternatives, runbook, limitations/runtime truth, glossary, and audit seal.

## States and Edge Cases

- No live Qwen: show fallback mode, skipped critic, and runtime truth; do not hide the run result.
- Tunnel down or API auth failed: render a network/configuration degraded state with no fake trace.
- Run failed: keep the status pill red and preserve the last known events.
- Evidence insufficient: root cause must say no automated root cause selected and route to human review.
- Readiness blocker: show formal blockers before any submission-ready claim.
- Long packet: keep copy button visible and use scrollable textbox behavior.

## Visual Evidence and References

Research checked on 2026-05-10 for Google Stitch / DESIGN.md compatibility:

- `google-labs-code/design.md`: official alpha-style structure uses YAML front matter plus Markdown rationale, linting, diff, and export concepts; this file follows that pattern without importing their example brand.
- `VoltAgent/awesome-design-md`: useful as a collection pattern, but it contains brand-inspired files and an explicit no-ownership claim, so InfraAgent uses only the organization idea, not any brand tokens.
- `kzhrknt/awesome-design-md-jp`: useful for typography/localization awareness; no CJK-specific tokens are needed for this English hackathon UI.
- `bergside/awesome-design-skills`: useful for separating design rules from agent skills; no external skill content is copied.
- `shaom/brand-to-design-md-skill`: useful source-aware extraction pattern; InfraAgent uses source notes and usage boundaries, not automated brand extraction.
- `hasi98/designpull`: useful reminder that visual extraction tools can be local/BYO-key; no remote designpull workflow is required for this repo.
- Lazyweb search returned no maintained GitHub repository through authenticated `gh search`; analogous visual-evidence paths were checked instead.
- `Dicklesworthstone/markdown_web_browser`: useful browser UI and visual provenance model for screenshot/OCR/markdown evidence; InfraAgent adopts the principle of visible provenance, not its scraping stack.
- `browser-use/workflow-use`: useful health/search workflow pattern with explicit early-development warning; InfraAgent does not depend on it for production or submission readiness.

## Do's and Don'ts

- Do keep the UI practical for incident commanders, SREs, AI platform owners, and judges.
- Do separate evidence timeline, node trace, root cause, scorecard, and final packet.
- Do use deterministic fixture truth notes whenever mock observability appears.
- Do make degraded states visible before a judge has to infer them.
- Do not expose raw vLLM in the UI.
- Do not use WebSocket or SSE patterns for the public path.
- Do not copy brand assets, layouts, colors, or screenshots from reference repositories.
- Do not present deterministic fixtures as production telemetry.
